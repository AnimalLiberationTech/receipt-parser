"""
Standalone HTTP API server for receipt-parser.
Run with: uvicorn local_server:app --reload --port 8000
"""
import os
import sys

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add src to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging

from src.handlers.add_barcodes import add_barcodes_handler
from src.handlers.home import home_handler
from src.handlers.link_shop import link_shop_handler
from src.handlers.parse_from_url import parse_from_url_handler
from src.handlers.shops import shops_handler
from src.helpers.common import get_template_path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Receipt Parser API",
    description="API for parsing receipts and managing shop data",
    version="1.0.0",
)

# Enable CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request models
class ParseFromUrlRequest(BaseModel):
    url: str
    user_id: str


class LinkShopRequest(BaseModel):
    url: str
    user_id: str
    receipt_id: str


class AddBarcodesRequest(BaseModel):
    shop_id: str
    items: list


# Routes
@app.get("/", response_class=HTMLResponse)
async def home():
    status, html_content = home_handler()
    return HTMLResponse(content=html_content, status_code=status.value)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/terms-of-service", response_class=HTMLResponse)
async def terms_of_service():
    try:
        with open(get_template_path("tos-en.html"), "r", encoding="utf8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Terms of service not found")


@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy():
    try:
        with open(get_template_path("privacy-policy-en.html"), "r", encoding="utf8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Privacy policy not found")


@app.post("/parse")
@app.post("/parse-from-url")
async def parse_from_url(request: ParseFromUrlRequest):
    status, response = parse_from_url_handler(request.url, request.user_id, logger)
    return JSONResponse(content=response, status_code=status.value)


@app.post("/link-shop")
async def link_shop(request: LinkShopRequest):
    status, response = link_shop_handler(
        request.url, request.user_id, request.receipt_id, logger
    )
    return JSONResponse(content=response, status_code=status.value)


@app.post("/add-barcodes")
async def add_barcodes(request: AddBarcodesRequest):
    status, response = add_barcodes_handler(request.shop_id, request.items, logger)
    return JSONResponse(content=response, status_code=status.value)


@app.get("/shops")
async def get_shops(
    request: Request,
    country_code: Optional[str] = None,
    company_id: Optional[str] = None,
    lat_min: Optional[float] = None,
    lat_max: Optional[float] = None,
    lon_min: Optional[float] = None,
    lon_max: Optional[float] = None,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
):
    query_params = {}
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

    status, response = shops_handler(query_params, logger)
    return JSONResponse(content=response, status_code=status.value)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

