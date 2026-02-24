"""
Local database API implementation.
Makes HTTP requests to a local pbapi server running on http://127.0.0.1:8000
"""

import json
from typing import Any, Dict
from urllib.parse import urlencode

import requests

from src.db.db_api_base import DbApiBase


class LocalDbApi(DbApiBase):
    """Database API implementation for local development environment."""

    def __init__(self, logger, base_url: str = "http://127.0.0.1:8000"):
        """
        Initialize Local DB API.

        Args:
            logger: Logger instance
            base_url: Base URL of the local pbapi server
        """
        self.logger = logger
        self.base_url = base_url.rstrip("/")

    def _execute(
        self,
        uri: str,
        method: str,
        payload: Dict[str, Any] | None = None,
        query: Dict[str, Any] | None = None,
    ) -> Dict[str, Any] | None:
        """
        Make a database API request to local pbapi server.

        Args:
            uri: The API endpoint path (e.g., "/receipt/get-by-id")
            method: HTTP method (GET, POST, etc.)
            payload: Request body data
            query: Query parameters

        Returns:
            Response data as a dictionary, or None on error
        """
        payload = payload or {}

        try:
            # Build full URL with query params if provided
            url = f"{self.base_url}{uri}"
            if query:
                separator = "&" if "?" in url else "?"
                url = f"{url}{separator}{urlencode(query, doseq=True)}"

            # Make request based on method
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(
                    url,
                    json=payload,
                    headers={"content-type": "application/json"},
                    timeout=10,
                )
            elif method.upper() == "PUT":
                response = requests.put(
                    url,
                    json=payload,
                    headers={"content-type": "application/json"},
                    timeout=10,
                )
            elif method.upper() == "DELETE":
                response = requests.delete(url, timeout=10)
            else:
                self.logger.error(f"Unsupported HTTP method: {method}")
                return None

            if response.status_code in [200, 201]:
                try:
                    return response.json()
                except (ValueError, json.JSONDecodeError) as e:
                    self.logger.error(
                        f"Failed to parse JSON response from local pbapi: {str(e)}"
                    )
                    return None

            self.logger.error(
                f"Error calling local pbapi: {response.status_code} - {response.text}"
            )
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout calling local pbapi at {self.base_url}")
        except requests.exceptions.ConnectionError:
            self.logger.error(
                f"Connection error calling local pbapi at {self.base_url}. "
                f"Is the pbapi server running?"
            )
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request exception calling local pbapi: {str(e)}")
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.logger.error(f"Unexpected exception calling local pbapi: {str(e)}")

        return None
