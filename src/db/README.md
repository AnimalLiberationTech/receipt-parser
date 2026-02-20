# Database API Architecture

This directory contains the database API abstraction layer that allows the application to work with different backend implementations based on the environment.

## Overview

The database API provides a unified interface for accessing the Plant-Based API (pbapi) database service, with different implementations for local development and production (Appwrite) environments.

## Architecture

```
src/db/
├── db_api_base.py       # Abstract base class defining the interface
├── appwrite_db_api.py   # Implementation for Appwrite environment
├── local_db_api.py      # Implementation for local development
└── __init__.py          # Package exports
```

## Usage

### In FastAPI Application

The `get_db_api()` dependency in `src/adapters/api/fastapi_app.py` automatically selects the correct implementation based on the `ENV_NAME` environment variable:

```python
from fastapi import Request
from src.db.db_api_base import DbApiBase

def get_db_api(request: Request) -> DbApiBase:
    env_name = os.environ.get("ENV_NAME", "").lower()
    
    if env_name == "local":
        # Use LocalDbApi for local development
        return LocalDbApi(logger, base_url="http://127.0.0.1:8000")
    else:
        # Use AppwriteDbApi for production
        return AppwriteDbApi(x_appwrite_key, logger)
```

### In Request Handlers

Use the db_api as a callable:

```python
# Make a GET request with query params
receipt = db_api("/receipt/get-by-id", "GET", None, {"receipt_id": receipt_id})

# Make a POST request with body
shop = db_api("/shop/get-or-create", "POST", shop_data)
```

## Implementations

### LocalDbApi

Used for local development. Makes direct HTTP requests to a local pbapi server.

**Environment variables:**
- `ENV_NAME=local`
- `LOCAL_PBAPI_URL` (optional, defaults to `http://127.0.0.1:8000`)

**Example:**
```bash
export ENV_NAME=local
export LOCAL_PBAPI_URL=http://127.0.0.1:8000
uvicorn src.adapters.api.fastapi_app:app --reload --port 8001
```

### AppwriteDbApi

Used for Appwrite deployment. Makes requests via Appwrite function executions to the pbapi function.

**Environment variables:**
- `ENV_NAME` (anything except "local")
- `APPWRITE_FUNCTION_PROJECT_ID`
- `APPWRITE_FUNCTION_API_ENDPOINT`

**Requires:**
- `x-appwrite-key` header in the request

## Interface

All implementations must inherit from `DbApiBase` and implement the `__call__` method:

```python
def __call__(
    self,
    uri: str,                           # API endpoint path
    method: str,                        # HTTP method (GET, POST, etc.)
    payload: Dict[str, Any] | None,     # Request body (optional)
    query: Dict[str, Any] | None,       # Query parameters (optional)
) -> Dict[str, Any] | None:             # Response data or None on error
    pass
```

## Adding a New Implementation

1. Create a new file in `src/db/` (e.g., `my_db_api.py`)
2. Inherit from `DbApiBase`
3. Implement the `__call__` method
4. Update `src/db/__init__.py` to export your class
5. Update `get_db_api()` in `fastapi_app.py` to support your implementation

## Testing

Test the db_api implementations:

```python
from src.db.local_db_api import LocalDbApi
from src.adapters.logger.default import DefaultLogger

logger = DefaultLogger(level=20).log
db_api = LocalDbApi(logger, base_url="http://127.0.0.1:8000")

# Make a request
result = db_api("/health", "GET", None, None)
print(result)
```

## Migration from Legacy Code

The old `src/helpers/appwrite.py` contained the database API logic directly. This has been refactored into:

- **`src/db/appwrite_db_api.py`**: AppwriteDbApi class (extracted from `appwrite_db_api()` function)
- **`src/db/local_db_api.py`**: New LocalDbApi class for local development
- **`src/db/db_api_base.py`**: Abstract base class for type safety
- **`src/helpers/appwrite.py`**: Now only contains Appwrite-specific helpers and decorators

The new structure provides:
- ✅ Better separation of concerns
- ✅ Environment-based selection
- ✅ Type safety with abstract base class
- ✅ Easier testing and mocking
- ✅ Support for local development without Appwrite

