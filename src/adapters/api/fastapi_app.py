import asyncio
import logging
import os
from http import HTTPStatus

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from src.adapters.doppler import load_doppler_secrets
from src.adapters.logger.appwrite import AppwriteLogger
from src.adapters.logger.default import DefaultLogger
from src.db.appwrite_db_api import AppwriteDbApi
from src.db.db_api_base import DbApiBase
from src.db.local_db_api import LocalDbApi
from src.handlers.link_shop import link_shop_handler
from src.handlers.parse_from_url import parse_from_url_handler
from src.schemas.common import ApiResponse, OsmType
from src.schemas.request_schemas import (
    ParseFromUrlRequest,
    LinkShopRequest,
)

load_doppler_secrets()


def get_logger(request: Request) -> logging.Logger:
    """Get logger based on environment."""
    if "appwrite_context" in request.scope:
        context = request.scope["appwrite_context"]
        return AppwriteLogger(context, level=logging.INFO).log

    return DefaultLogger(level=logging.DEBUG).log


def get_db_api(request: Request) -> DbApiBase:
    """
    Get database API implementation based on the environment.

    - ENV_NAME=local: Uses LocalDbApi (http://127.0.0.1:8000)
    - Otherwise: Uses AppwriteDbApi
    """
    env_name = os.environ.get("ENV_NAME", "").lower()
    logger = get_logger(request)

    if env_name == "local":
        # Use local pbapi server
        base_url = os.environ.get("LOCAL_PBAPI_URL", "http://127.0.0.1:8000")
        logger.info(f"Using LocalDbApi with base URL: {base_url}")
        return LocalDbApi(logger, base_url=base_url)
    else:
        # Use Appwrite pbapi function
        if "appwrite_context" in request.scope:
            context = request.scope["appwrite_context"]
            x_appwrite_key = context.req.headers.get("x-appwrite-key", "")
        else:
            x_appwrite_key = request.headers.get("x-appwrite-key", "")

        logger.info("Using AppwriteDbApi")
        return AppwriteDbApi(x_appwrite_key, logger)


app = FastAPI(
    title="Receipt Parser API",
    description="API for parsing receipts and managing shop data",
    version="0.0.1",
)

# Enable CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def with_status(api_response: ApiResponse, response: Response) -> ApiResponse:
    """Align HTTP response status with ApiResponse payload."""
    response.status_code = int(api_response.status_code)
    return api_response


@app.post("/parse", response_model=ApiResponse, tags=["parse"])
@app.post("/parse-from-url", response_model=ApiResponse, tags=["parse"])
async def parse_from_url(
    request: ParseFromUrlRequest,
    req: Request,
    response: Response,
    logger=Depends(get_logger),
):
    logger.info(f"Parse from URL: {request.url}")

    if not request.url:
        return with_status(
            ApiResponse(status_code=HTTPStatus.BAD_REQUEST, detail="URL is required"),
            response,
        )

    db_api = get_db_api(req)
    api_response = await parse_from_url_handler(
        request.url, request.user_id, logger, db_api
    )
    return with_status(api_response, response)


@app.post("/link-shop", response_model=ApiResponse, tags=["link-shop"])
async def link_shop(
    request: LinkShopRequest,
    req: Request,
    response: Response,
    logger=Depends(get_logger),
):
    """Link a shop to a receipt using OSM data."""
    logger.info(f"Link shop: OSM {request.osm_type}:{request.osm_key}")

    try:
        osm_type = OsmType(request.osm_type)
    except ValueError:
        return with_status(
            ApiResponse(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid OSM type"),
            response,
        )

    try:
        osm_key = int(request.osm_key)
    except ValueError:
        return with_status(
            ApiResponse(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid OSM key"),
            response,
        )

    db_api = get_db_api(req)
    api_response = await asyncio.to_thread(
        link_shop_handler, osm_type, osm_key, request.receipt_id, logger, db_api
    )
    return with_status(api_response, response)


@app.get("/", response_model=ApiResponse, tags=["home"])
async def home(response: Response, logger=Depends(get_logger)):
    logger.info("Parser home endpoint called")
    api_response = await health(logger)
    return with_status(api_response, response)


@app.get("/health", response_model=ApiResponse, tags=["health"])
async def health(logger=Depends(get_logger)):
    logger.info("Parser health endpoint called")
    return ApiResponse(
        status_code=status.HTTP_200_OK,
        detail="Parser health check successful",
    )


@app.get("/health/deep-ping", response_model=ApiResponse, tags=["health"])
async def deep_ping(response: Response, logger=Depends(get_logger)):
    logger.info("Parser deep ping endpoint called")
    await asyncio.sleep(1)
    api_response = ApiResponse(
        status_code=status.HTTP_200_OK,
        detail="Parser deep ping successful",
    )
    return with_status(api_response, response)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


@app.get("/openapi.json", include_in_schema=False)
async def get_openapi():
    return app.openapi()
