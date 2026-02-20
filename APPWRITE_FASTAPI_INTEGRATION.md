# Appwrite FastAPI Integration

This document describes how the FastAPI application is served on Appwrite using the `AppwriteFastAPIAdapter`.

## Architecture

The FastAPI application can be served in two ways:

### 1. Local Development (Plain FastAPI)
```
Client → FastAPI App → Handlers → Database
         (Uvicorn Server)
```

**Usage:**
```bash
export ENV_NAME=local
uvicorn src.adapters.api.fastapi_app:app --reload --port 8001
```

### 2. Appwrite Deployment (ASGI → Appwrite Adapter)
```
Appwrite Function Context → AppwriteFastAPIAdapter → FastAPI App → Handlers → Database
     (Appwrite Runtime)         (Translation Layer)
```

**Usage:**
The Appwrite function executes `src/adapters/appwrite_functions.py` as the entry point.

## Files

### `src/adapters/api/fastapi_app.py`
The main FastAPI application with all endpoints:
- `POST /parse` - Parse receipt from URL
- `POST /link-shop` - Link OSM shop to receipt
- `POST /add-barcodes` - Add barcodes to items
- `GET /shops` - List shops with filters
- `GET /health` - Health check
- Automatic db_api selection based on `ENV_NAME`

**Key feature:** Environment-aware database API selection
- `ENV_NAME=local` → LocalDbApi (direct HTTP to http://127.0.0.1:8000)
- Otherwise → AppwriteDbApi (via Appwrite pbapi function)

### `src/adapters/api/appwrite_fastapi_adapter.py`
Translates between Appwrite context and ASGI protocol:
- Converts Appwrite request to ASGI scope
- Implements ASGI `receive()` and `send()` callables
- Captures response from FastAPI app
- Returns response via Appwrite context methods

**Process:**
```
1. Appwrite passes context (req, res) to adapter
2. Adapter builds ASGI scope from context.req
3. Adapter implements receive() with request body
4. Adapter calls FastAPI app with (scope, receive, send)
5. FastAPI calls send() with response chunks
6. Adapter captures response and calls context.res.json()
```

### `src/adapters/appwrite_functions.py`
Appwrite function entry point:
- Loads environment and secrets
- Creates AppwriteLogger from Appwrite context
- Instantiates AppwriteFastAPIAdapter
- Routes all requests through FastAPI

**Entry point:** `main(context)` or `sync_main(context)`

### `src/helpers/appwrite.py`
Appwrite-specific helpers:
- `AppwriteLogger` - Logs via Appwrite context
- `CORS_HEADERS` - Constant with CORS configuration
- `build_db_api()` - Creates AppwriteDbApi from context
- `with_db_api()` - Decorator for old Appwrite handlers
- `parse_json_body()` - Decorator for JSON parsing

## How It Works

### Local Development Flow
```python
# User runs:
$ uvicorn src.adapters.api.fastapi_app:app --reload --port 8001

# Uvicorn starts FastAPI
# User makes request:
$ curl -X POST http://localhost:8001/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "...", "user_id": "..."}'

# FastAPI processes request directly
# get_db_api() detects ENV_NAME=local
# Returns LocalDbApi (HTTP client)
# Handler gets db_api and processes normally
```

### Appwrite Deployment Flow
```
1. Appwrite function runtime executes appwrite_functions.py:main()

2. main(context) creates AppwriteFastAPIAdapter

3. adapter.handle(context) is awaited:
   a. Builds ASGI scope from context.req
   b. Implements receive() → context.req.body
   c. Calls FastAPI app(scope, receive, send)
   d. FastAPI processes request normally
   
4. FastAPI route (e.g., /parse):
   a. get_db_api(request) is called
   b. Detects ENV_NAME != local
   c. Returns AppwriteDbApi with x-appwrite-key
   d. Calls handler with db_api
   
5. Handler makes db_api calls:
   a. db_api() calls AppwriteDbApi.__call__()
   b. Makes HTTP request to pbapi function
   c. Returns response
   
6. Handler returns ApiResponse

7. FastAPI serializes response

8. send() callable captures response chunks

9. adapter.handle() calls context.res.json()

10. Appwrite returns response to client
```

## Environment Configuration

### Local Development
```bash
# .env or shell
export ENV_NAME=local
export LOCAL_PBAPI_URL=http://127.0.0.1:8000  # optional
```

### Appwrite Deployment
```bash
# Set via Appwrite dashboard or deploy config
ENV_NAME=dev  # or prod, stage
APPWRITE_FUNCTION_PROJECT_ID=<your-project-id>
APPWRITE_FUNCTION_API_ENDPOINT=<your-endpoint>
```

## Error Handling

Both paths handle errors consistently:

1. **Request validation errors** (e.g., invalid UUID):
   - Returns `ApiResponse` with 400 status
   - FastAPI serializes to JSON
   - Sent to client

2. **Handler errors** (e.g., receipt not found):
   - Handler returns `ApiResponse` with appropriate status
   - Propagates normally

3. **Adapter errors** (Appwrite context issues):
   - Caught in `appwrite_functions.py:main()`
   - Returns 500 error response via context.res.json()

4. **FastAPI errors** (e.g., route not found):
   - FastAPI returns 404
   - Adapter captures and returns via context.res.json()

## CORS Headers

All responses include CORS headers:
```python
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, x-appwrite-key",
}
```

Applied by:
- FastAPI middleware (local development)
- Adapter response (Appwrite deployment)

## Testing

### Test with Mock Appwrite Context
```python
from unittest.mock import MagicMock
from src.adapters.api.appwrite_fastapi_adapter import AppwriteFastAPIAdapter
from src.adapters.api.fastapi_app import app
import asyncio

# Mock Appwrite context
class MockRequest:
    method = "GET"
    path = "/health"
    headers = {"x-appwrite-key": "test"}
    body = None
    url = "/health"

class MockResponse:
    def json(self, data, status, headers=None):
        return {"status": status, "data": data, "headers": headers}

context = MagicMock()
context.req = MockRequest()
context.res = MockResponse()

# Test adapter
adapter = AppwriteFastAPIAdapter(app)
result = asyncio.run(adapter.handle(context))
print(result)
```

### Test Locally
```bash
# Terminal 1: Start pbapi server
cd ../pbapi
uvicorn app:app --port 8000

# Terminal 2: Start receipt parser
export ENV_NAME=local
uvicorn src.adapters.api.fastapi_app:app --reload --port 8001

# Terminal 3: Make requests
curl http://localhost:8001/health
curl -X POST http://localhost:8001/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "...", "user_id": "..."}'
```

## Migration Notes

Previously, Appwrite handlers used decorators:
```python
@with_db_api
@parse_json_body
def handle_parse_from_url(body, logger, db_api):
    ...
```

Now, all requests go through FastAPI:
```python
@app.post("/parse")
async def parse_from_url(request: ParseFromUrlRequest, req: Request, logger=Depends(get_logger)):
    db_api = get_db_api(req)
    return parse_from_url_handler(request.url, request.user_id, logger, db_api)
```

Benefits:
- ✅ Single codebase for local and Appwrite
- ✅ OpenAPI documentation
- ✅ Automatic request validation
- ✅ Easier testing
- ✅ Standard FastAPI patterns

## Future Improvements

1. **Response compression**: Add gzip compression for Appwrite responses
2. **Streaming**: Support streaming responses (e.g., for large receipts)
3. **Middleware**: Add logging, metrics, authentication middleware
4. **Caching**: Cache pbapi responses when appropriate
5. **Rate limiting**: Implement rate limiting per user/endpoint

