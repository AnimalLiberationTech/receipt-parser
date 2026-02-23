"""
Base class for database API implementations.
Defines the interface that all db_api implementations must follow.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict


class DbApiBase(ABC):
    """Abstract base class for database API implementations."""

    @abstractmethod
    def _execute(
        self,
        uri: str,
        method: str,
        payload: Dict[str, Any] | None = None,
        query: Dict[str, Any] | None = None,
    ) -> Dict[str, Any] | None:
        """
        Execute the actual database API request (implemented by subclasses).

        Args:
            uri: The API endpoint path (e.g., "/receipt/get-by-id")
            method: HTTP method (GET, POST, etc.)
            payload: Request body data
            query: Query parameters

        Returns:
            Response data as a dictionary, or None on error
        """
        pass

    def __call__(
        self,
        uri: str,
        method: str,
        payload: Dict[str, Any] | None = None,
        query: Dict[str, Any] | None = None,
    ) -> Dict[str, Any] | None:
        """
        Make a database API request.

        This method can be called from sync code and will work correctly.
        When used in async context, it returns a coroutine that must be awaited.

        Args:
            uri: The API endpoint path (e.g., "/receipt/get-by-id")
            method: HTTP method (GET, POST, etc.)
            payload: Request body data
            query: Query parameters

        Returns:
            Response data as a dictionary, or None on error
        """
        # Check if we're in an async context
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context, return a coroutine
            return self._async_execute(uri, method, payload, query)
        except RuntimeError:
            # No event loop, execute synchronously
            return self._execute(uri, method, payload, query)

    async def _async_execute(
        self,
        uri: str,
        method: str,
        payload: Dict[str, Any] | None = None,
        query: Dict[str, Any] | None = None,
    ) -> Dict[str, Any] | None:
        """
        Async wrapper that runs _execute in a thread pool to avoid blocking.

        Args:
            uri: The API endpoint path
            method: HTTP method
            payload: Request body data
            query: Query parameters

        Returns:
            Response data as a dictionary, or None on error
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self._execute, uri, method, payload, query
        )
