import json
import os
from uuid import UUID

from cachecontrol import CacheControl
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from requests import Session
from time import time

from src.adapters.db.cosmos_db_core import init_db_session
from src.helpers.common import is_localhost
from src.schemas.common import TableName
from src.schemas.user import User
from src.schemas.user_auth import GoogleUserAuth
from src.schemas.user_identity import IdentityProvider, UserIdentity
from src.schemas.user_session import GoogleUserSession, UserSessionCookie

GOOGLE_CALLBACK_URI = ".auth/login/google/callback"


class GoogleAuth:
    user: GoogleUserAuth | None = None

    def __init__(self, logger):
        self.logger = logger
        if is_localhost():
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        self.secrets_file_path = os.path.join(".google_client_secret.json")

        logger.info("WEBSITE_HOSTNAME: " + os.environ["WEBSITE_HOSTNAME"])

        app_host_protocol = "http" if is_localhost() else "https"
        self.flow = Flow.from_client_secrets_file(
            client_secrets_file=self.secrets_file_path,
            scopes=[
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email",
                "openid",
            ],
            redirect_uri=f"{app_host_protocol}://{os.environ['WEBSITE_HOSTNAME']}/{GOOGLE_CALLBACK_URI}",
        )
        self.db_session = init_db_session(logger)

    def verify_token(self, url: str) -> None:
        self.flow.fetch_token(authorization_response=url)
        credentials = self.flow.credentials
        request_session = Session()
        cached_session = CacheControl(request_session)
        token_request = Request(session=cached_session)

        data = id_token.verify_oauth2_token(
            id_token=credentials._id_token,  # pylint: disable=protected-access
            request=token_request,
            audience=self.get_google_client_id(),
        )
        if data and time() < data["exp"]:
            self.user = GoogleUserAuth.from_token(data)

    def create_session(self) -> (str, UserSessionCookie):
        auth_url, state = self.flow.authorization_url()
        user_session = GoogleUserSession(state=state)

        self.db_session.use_table(TableName.USER_SESSION)
        session_id = self.db_session.create_one(user_session.model_dump(mode="json"))

        return auth_url, UserSessionCookie(
            session_id=UUID(session_id), identity_provider=IdentityProvider.GOOGLE
        )

    def get_new_session(self, session_id: UUID) -> GoogleUserSession | None:
        self.db_session.use_table(TableName.USER_SESSION)
        session = self.db_session.read_one(
            str(session_id), partition_key=IdentityProvider.GOOGLE
        )
        self.logger.info(session)
        if session:
            return GoogleUserSession(id=session_id, state=session["state"])
        return None

    def update_session(
        self, session: GoogleUserSession, google_auth: GoogleUserAuth
    ) -> GoogleUserSession:
        self.db_session.use_table(TableName.USER_IDENTITY)
        identity = self.db_session.read_one(
            google_auth.google_id, partition_key=IdentityProvider.GOOGLE
        )
        if identity:
            user_id = identity["user_id"]
        else:
            self.db_session.use_table(TableName.USER)
            user = User(email=google_auth.email, name=google_auth.name, id=None)
            user_id = self.db_session.create_one(user.model_dump(mode="json"))

            identity = UserIdentity(
                id=google_auth.google_id,
                provider=IdentityProvider.GOOGLE,
                user_id=UUID(user_id),
            ).model_dump(mode="json")
            self.db_session.use_table(TableName.USER_IDENTITY)
            self.db_session.create_one(identity)

        session.user_id = UUID(user_id)
        session.user_name = google_auth.name
        self.db_session.use_table(TableName.USER_SESSION)
        self.logger.info(session.model_dump())
        self.db_session.update_one(str(session.id), session.model_dump(mode="json"))
        return session

    def get_google_client_id(self) -> str:
        with open(self.secrets_file_path, "r", encoding="utf8") as file:
            return json.loads(file.read())["web"]["client_id"]
