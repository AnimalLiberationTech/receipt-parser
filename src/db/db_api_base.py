"""
Base class for database API implementations.
Defines the interface that all db_api implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class DbApiBase(ABC):
    """Abstract base class for database API implementations."""

    @abstractmethod
    def __call__(
        self,
        uri: str,
        method: str,
        payload: Dict[str, Any] | None = None,
        query: Dict[str, Any] | None = None,
    ) -> Dict[str, Any] | None:
        """
        Make a database API request.

        Args:
            uri: The API endpoint path (e.g., "/receipt/get-by-id")
            method: HTTP method (GET, POST, etc.)
            payload: Request body data
            query: Query parameters

        Returns:
            Response data as a dictionary, or None on error
        """
        pass
