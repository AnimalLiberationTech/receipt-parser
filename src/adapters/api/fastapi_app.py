import logging
import os
import time
from http import HTTPStatus
from typing import Dict, Any

from fastapi import FastAPI, Depends, Query
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
from src.handlers.add_barcodes import add_barcodes_handler
from src.handlers.link_shop import link_shop_handler
from src.handlers.parse_from_url import parse_from_url_handler
from src.handlers.shops import shops_handler
from src.schemas.common import ApiResponse, OsmType
from src.schemas.request_schemas import (
    ParseFromUrlRequest,
    LinkShopRequest,
    AddBarcodesRequest,
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
    """Parse a receipt from a URL."""
    logger.info(f"Parse from URL: {request.url}")

    if not request.url:
        return with_status(
            ApiResponse(status_code=HTTPStatus.BAD_REQUEST, detail="URL is required"),
            response,
        )

    db_api = get_db_api(req)
    api_response = parse_from_url_handler(request.url, request.user_id, logger, db_api)
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
    api_response = link_shop_handler(osm_type, osm_key, request.receipt_id, logger, db_api)
    return with_status(api_response, response)


@app.post("/add-barcodes", response_model=ApiResponse, tags=["barcodes"])
async def add_barcodes(
    request: AddBarcodesRequest,
    response: Response,
    logger=Depends(get_logger),
):
    """Add barcodes to shop items."""
    logger.info(f"Add barcodes for shop: {request.shop_id}")
    api_response = add_barcodes_handler(request.shop_id, request.items, logger)
    return with_status(api_response, response)


@app.get("/shops", response_model=ApiResponse, tags=["shops"])
async def get_shops(
    country_code: str | None = Query(None),
    company_id: str | None = Query(None),
    lat_min: float | None = Query(None),
    lat_max: float | None = Query(None),
    lon_min: float | None = Query(None),
    lon_max: float | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    response: Response = None,
    logger=Depends(get_logger),
):
    """Get shops with optional filtering."""
    logger.info("Get shops endpoint called")

    query_params: Dict[str, Any] = {}
    if country_code:
        query_params["country_code"] = country_code
    if company_id:
        query_params["company_id"] = company_id
    if lat_min is not None:
        query_params["lat_min"] = lat_min
    if lat_max is not None:
        query_params["lat_max"] = lat_max
    if lon_min is not None:
        query_params["lon_min"] = lon_min
    if lon_max is not None:
        query_params["lon_max"] = lon_max
    query_params["limit"] = limit
    query_params["offset"] = offset

    api_response = shops_handler(query_params, logger)
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
    time.sleep(1)
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
