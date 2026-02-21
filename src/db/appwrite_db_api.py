"""
Appwrite database API implementation.
Communicates with the pbapi Appwrite function to access the database.
"""

import json
import os
from typing import Any, Dict
from urllib.parse import urlencode

import requests

from src.db.db_api_base import DbApiBase


class AppwriteDbApi(DbApiBase):
    """Database API implementation for Appwrite environment."""

    def __init__(self, x_appwrite_key: str, logger):
        """
        Initialize Appwrite DB API.

        Args:
            x_appwrite_key: Appwrite API key for authentication
            logger: Logger instance
        """
        self.x_appwrite_key = x_appwrite_key
        self.logger = logger
        self.api_endpoint = os.environ.get("APPWRITE_FUNCTION_API_ENDPOINT")
        self.project_id = os.environ.get("APPWRITE_FUNCTION_PROJECT_ID")

    def __call__(
        self,
        uri: str,
        method: str,
        payload: Dict[str, Any] | None = None,
        query: Dict[str, Any] | None = None,
    ) -> Dict[str, Any] | None:
        """
        Make a database API request via Appwrite pbapi function.

        Args:
            uri: The API endpoint path (e.g., "/receipt/get-by-id")
            method: HTTP method (GET, POST, etc.)
            payload: Request body data
            query: Query parameters

        Returns:
            Response data as a dictionary, or None on error
        """
        payload = payload or {}
        headers = {
            "x-appwrite-key": self.x_appwrite_key,
            "x-appwrite-project": self.project_id,
        }

        try:
            # Build path with query params if provided
            path = uri
            if query:
                separator = "&" if "?" in path else "?"
                path = f"{path}{separator}{urlencode(query, doseq=True)}"

            # Prepare execution payload for Appwrite function
            execution_payload = {
                "method": method,
                "path": path,
                "body": json.dumps(payload),
                "headers": {"content-type": "application/json"},
            }

            # Call pbapi via Appwrite function execution
            response = requests.post(
                f"{self.api_endpoint}/functions/pbapi/executions",
                json=execution_payload,
                headers=headers,
                timeout=10,
            )

            if response.status_code in [200, 201]:
                try:
                    result = response.json()
                    # Appwrite returns an execution object, extract responseBody
                    if "responseBody" in result:
                        try:
                            return json.loads(result["responseBody"])
                        except (ValueError, json.JSONDecodeError):
                            return result["responseBody"]
                    return result
                except (ValueError, json.JSONDecodeError) as e:
                    self.logger.error(
                        f"Failed to parse JSON response from pbapi: {str(e)}"
                    )
                    return None

            self.logger.error(
                f"Error calling pbapi: {response.status_code} - {response.text}"
            )
        except requests.exceptions.Timeout:
            self.logger.error("Timeout calling pbapi")
        except requests.exceptions.ConnectionError:
            self.logger.error("Connection error calling pbapi")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request exception calling pbapi: {str(e)}")
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.logger.error(f"Unexpected exception calling pbapi: {str(e)}")

        return None
