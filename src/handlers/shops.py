import os
from http import HTTPStatus
from typing import Any

from src.schemas.common import TableName

# Chisinau area approximate bounding box
CHISINAU_LAT_MIN = 46.95
CHISINAU_LAT_MAX = 47.07
CHISINAU_LON_MIN = 28.77
CHISINAU_LON_MAX = 28.90


def init_postgres_session(logger):
    """Initialize PostgreSQL database session."""
    env_name = os.environ.get("ENV_NAME", "local")
    # return PostgreSQLCoreAdapter(EnvType(env_name), logger)


def shops_handler(query_params: dict[str, Any], logger) -> tuple[HTTPStatus, dict]:
    """
    Get shops with optional filtering by query parameters.

    Supported query params:
    - country_code: filter by country code (e.g., 'md')
    - company_id: filter by company ID
    - lat_min, lat_max, lon_min, lon_max: bounding box for location (optional)
    - limit: max number of results (default 50)
    - offset: pagination offset (default 0)
    """
    session = init_postgres_session(logger)
    session.use_table(TableName.SHOP)

    # Build where clause from query params
    where = {}

    if "country_code" in query_params:
        where["country_code"] = query_params["country_code"]

    if "company_id" in query_params:
        where["company_id"] = query_params["company_id"]

    # Get limit and offset
    try:
        limit = int(query_params.get("limit", 50))
        limit = min(limit, 100)  # Cap at 100
    except (ValueError, TypeError):
        limit = 50

    try:
        offset = int(query_params.get("offset", 0))
    except (ValueError, TypeError):
        offset = 0

    # Check if location filtering is requested
    has_location_filter = any(
        key in query_params for key in ["lat_min", "lat_max", "lon_min", "lon_max"]
    )

    # Read shops from database
    shops = session.read_many(where if where else None, limit=limit + offset)

    # Apply location filter only if explicitly requested
    if has_location_filter:
        try:
            lat_min = float(query_params.get("lat_min", CHISINAU_LAT_MIN))
            lat_max = float(query_params.get("lat_max", CHISINAU_LAT_MAX))
            lon_min = float(query_params.get("lon_min", CHISINAU_LON_MIN))
            lon_max = float(query_params.get("lon_max", CHISINAU_LON_MAX))
        except (ValueError, TypeError):
            lat_min, lat_max = CHISINAU_LAT_MIN, CHISINAU_LAT_MAX
            lon_min, lon_max = CHISINAU_LON_MIN, CHISINAU_LON_MAX

        filtered_shops = []
        for shop in shops:
            osm_data = shop.get("osm_data", {})
            if osm_data:
                try:
                    lat = float(osm_data.get("lat", 0))
                    lon = float(osm_data.get("lon", 0))
                    if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                        filtered_shops.append(shop)
                except (ValueError, TypeError):
                    continue
        shops = filtered_shops

    # Apply offset and limit
    total = len(shops)
    result_shops = shops[offset : offset + limit]

    return HTTPStatus.OK, {
        "items": result_shops,
        "total": total,
        "limit": limit,
        "offset": offset,
    }
