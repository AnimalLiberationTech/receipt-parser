# Receipt Parser Service

The goal of this service, as implied by its name, is to speed up the process of updating products' availability. 
This is achieved by parsing receipts and linking products to the corresponding shops in the database. 
We begin by addressing the more accessible digital receipts, before progressing to handling physical ones.


## Running the service locally

### Quick Start (Docker)
```bash
# Start PostgreSQL + migrate to legacy schema + build functions
./local-appwrite-deploy.sh

# Stop all services
./local-appwrite-deploy.sh --down
```

### Manual Setup
1. Install Python 3.12
2. Install [uv](https://docs.astral.sh/uv/)
3. Run `uv sync`
4. Create database and required tables (see [Database Migrations](#database-migrations))
5. Run Azure Functions locally:
   ```bash
   cd azure_functions
   func start
   ```

### Local Appwite Deployment Options
```bash
# Deploy with specific migration target
./local-appwrite-deploy.sh --target initial_001_schema

# Skip Docker (use existing PostgreSQL)
./local-appwrite-deploy.sh --skip-docker

# Skip migration
./local-appwrite-deploy.sh --skip-migration

# Skip function deployment
./local-appwrite-deploy.sh --skip-functions
```

### Testing Functions Locally
```bash
# Run a function with the local runner
uv run python local_appwrite_functions.py parse_from_url \
  --body '{"url": "https://mev.sfs.md/receipt/...", "user_id": "123e4567-e89b-12d3-a456-426614174000"}'
```

### Parse Receipt from URL logic flow
- Validate input: require `url` and a valid UUID `user_id`.
- Create `ReceiptParser` with `logger`, `user_id`, `url`, and `db_api`.
- Reject unsupported receipt hosts.
- Try to fetch an existing receipt from storage by URL.
- If found, return it; otherwise fetch HTML for the receipt URL.
- Parse HTML, build the receipt model, persist via `db_api`.
- Return `200` with the receipt payload; map validation errors to `400`, unexpected errors to `500`.


## Database Migrations

The project supports both CosmosDB and PostgreSQL databases.

### CosmosDB Migration
```bash
uv run python db_migration.py --env dev --db cosmos --appinsights "<app-insights-connection-string>"
```

### PostgreSQL Migration

PostgreSQL migrations use [Alembic](https://alembic.sqlalchemy.org/) for version control, allowing you to upgrade and downgrade database schema versions. A backup is automatically created before each migration.

#### Migration Structure

The migrations are organized as follows:
- `legacy_000_schema` - The original Plante database schema (extracted from pg_dump backup)
- `initial_001_schema` - New receipt-parser schema additions based on `src/schemas`

(almost) every migration consists of:
- `<name>.py` - Alembic migration file that loads SQL files
- `<name>_up.sql` - SQL for upgrade
- `<name>_down.sql` - SQL for downgrade

#### Setup Environment Variables
```bash
export DEV_POSTGRES_HOST=localhost
export DEV_POSTGRES_PORT=5432
export DEV_POSTGRES_DB=pbapi_local
export DEV_POSTGRES_USER=postgres
export DEV_POSTGRES_PASSWORD=postgres
```

#### Migration Commands
_(make sure PostgreSQL creds are set in the .env file)_

**Run migrations (upgrade to latest):**
```bash
uv run python db_migration.py --env $ENV_NAME --db postgres --action up
```

**Downgrade one revision:**
```bash
uv run python db_migration.py --env dev --db postgres --action down
```

**Downgrade to specific revision:**
```bash
uv run python db_migration.py --env $ENV_NAME --db postgres --action down --revision legacy_000_schema
```

**Show migration history:**
```bash
uv run python db_migration.py --env $ENV_NAME --db postgres --action history
```

**Show current revision:**
```bash
uv run python db_migration.py --env $ENV_NAME --db postgres --action current
```

**Create new migration:**
```bash
uv run python db_migration.py --env $ENV_NAME --db postgres --action create -m "add_new_column"
```

**Skip backup (not recommended for production):**
```bash
uv run python db_migration.py --env $ENV_NAME --db postgres --action up --no-backup
```

### Database Backup Utility

The backup utility creates SQL dumps before migrations and can be used standalone:

```bash
# Create a backup
uv run python db_backup.py backup --env $ENV_NAME

# List available backups
uv run python db_backup.py list --env $ENV_NAME

# Restore from backup
uv run python db_backup.py restore --env $ENV_NAME --file backups/receipt_parser_dev_20260103_120000.sql

# Cleanup old backups (keep last 10)
uv run python db_backup.py cleanup --env $ENV_NAME --keep 10
```

#### Splitting a pg_dump backup

If you need to extract schema from a full pg_dump backup:
```bash
# Split into schema and data files
python3 split_backup.py

# Generate down migration from schema file
python3 split_backup.py --generate-down
```

### Migration Options
- `--env`: Required. One of `prod`, `stage`, `dev`, `test`, `local`
- `--db`: Database type. Either `cosmos` or `postgres` (default: `postgres`)
- `--action`: Migration action. One of `up`, `down`, `history`, `current`, `create` (default: `up`)
- `--revision`: Target revision for up/down (default: `head` for up, `-1` for down)
- `--message`, `-m`: Migration message (required for `create` action)
- `--no-backup`: Skip backup before migration
- `--appinsights`: Azure Application Insights connection string (required for CosmosDB)


## Deploying to Azure Functions
1. Install [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/)
2. Verify Azure CLI was installed `az --version`
3. `az login`
4. Deploy app to prod `func azure functionapp publish plante-receipt-parser`


## Deploying as HTTP API

### Option 1: FastAPI Server (Standalone)

Run the API server directly using FastAPI/Uvicorn:

```bash
# Development (with auto-reload)
uv run uvicorn local_server:app --reload --port 8000

# Production
uv run uvicorn local_server:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with automatic OpenAPI docs at `/docs`.

### Option 2: Appwrite Functions

Deploy to Appwrite Cloud or self-hosted:

```bash
# Install Appwrite CLI
npm install -g appwrite-cli

# Login and deploy
appwrite login
appwrite deploy function
```

### Option 3: Docker

```bash
# Build and run
docker build -t receipt-parser-api .
docker run -p 8000:8000 --env-file .env receipt-parser-api
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET | `/health` | Health check |
| GET | `/shops` | List shops (with query filters) |
| POST | `/parse-from-url` | Parse receipt from URL |
| POST | `/link-shop` | Link shop to receipt |
| POST | `/add-barcodes` | Add barcodes to products |
| GET | `/terms-of-service` | Terms of service |
| GET | `/privacy-policy` | Privacy policy |


## Running tests

### Unit tests
Run `python -m unittest discover -s src/tests/unit`

### Integration tests
1. Set up environment variables locally:
    - `TEST_COSMOS_DB_ACCOUNT_HOST=https://{Cosmos-DB-account-name}.documents.azure.com:443/`
    - `TEST_COSMOS_DB_ACCOUNT_KEY={key}`
    - `TEST_COSMOS_DB_DATABASE_ID=PlanteTest`
2. Create database and required tables by running `python db_migration.py` with `EnvType.TEST`
3. Run `python -m unittest discover -s src/tests/integration`

### Functional tests
1. Set up environment variables locally:
    - `TEST_COSMOS_DB_ACCOUNT_HOST=https://{Cosmos-DB-account-name}.documents.azure.com:443/`
    - `TEST_COSMOS_DB_ACCOUNT_KEY={key}`
    - `TEST_COSMOS_DB_DATABASE_ID=PlanteTest`
    - `WEBSITE_HOSTNAME=plante-receipts-test.azurewebsites.net`
2. Deploy service to test environment `func azure functionapp publish plante-receipt-parser-test`
   1. If the service was never deployed before, add these values to Function App Configuration:
      - `TEST_COSMOS_DB_ACCOUNT_HOST=https://{Cosmos-DB-account-name}.documents.azure.com:443/`
      - `TEST_COSMOS_DB_ACCOUNT_KEY={key}`
      - `TEST_COSMOS_DB_DATABASE_ID=PlanteTest`
      - `ENV_NAME=test`
3. Run `python -m unittest discover -s src/tests/functional`


## Architecture
The code aims at modularity and loose coupling. 
External interfaces like database and endpoint handlers should be easily replaceable.
Schemas aim to add predictability and consistency to the domain objects 
but not at the expense of flexibility.

[Architecture and infrastructure diagram](https://miro.com/app/board/uXjVNo2NxpI=/?share_link_id=577664435504)


## Code style
To check the code formatting, run `pylint src function_app.py`  
To fix most of the formatting issues, run `black src function_app.py`