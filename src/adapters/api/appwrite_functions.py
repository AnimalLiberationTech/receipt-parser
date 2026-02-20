import asyncio
import os
import sys

current_dir = os.path.dirname(__file__)  # src/adapters/api/
base_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from src.adapters.api.appwrite_fastapi_adapter import AppwriteFastAPIAdapter
from src.adapters.api.fastapi_app import app as fastapi_app
from src.adapters.doppler import load_doppler_secrets
from src.helpers.appwrite import AppwriteLogger, CORS_HEADERS

load_doppler_secrets()


async def main(context):
    """
    Main entry point for Appwrite function.

    Serves the FastAPI application via the AppwriteFastAPIAdapter,
    which translates between Appwrite context and ASGI.
    """
    logger = AppwriteLogger(context)
    logger.info(f"{context.req.method} {context.req.path}")

    try:
        adapter = AppwriteFastAPIAdapter(fastapi_app)
        return await adapter.handle(context)
    except Exception as e:
        logger.error(f"Error serving FastAPI app: {str(e)}")
        return context.res.json(
            {"error": "Internal server error", "detail": str(e)},
            500,
            CORS_HEADERS,
        )


def sync_main(context):
    """Synchronous wrapper for Appwrite function context."""
    try:
        return asyncio.run(main(context))
    except RuntimeError:
        # Event loop already exists, use it
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(main(context))
