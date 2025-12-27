# Receipt Parser Service

The objective of this service, as implied by its name, is to speed up the process of updating products' availability. 
This is achieved by parsing receipts and linking products to the corresponding shops in the database. 
We begin by addressing the more accessible digital receipts, before progressing to handling physical ones.


## Running the service locally
1. Install Python 3.11
2. Install [Pipenv](https://pipenv.pypa.io/en/latest/)
3. Run `export PIPENV_VENV_IN_PROJECT=1 && pipenv sync --dev`
4. Run `pipenv shell`
5. Create database and required tables `python src/migrations.py` with `EnvType.DEV`
6. Run `func start`


## Deploying to Azure Functions
1. Install [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/)
2. Verify Azure CLI was installed `az --version`
3. `az login`
4. Deploy app to prod `func azure functionapp publish plante-receipt-parser`


## Running tests

### Unit tests
Run `python -m unittest discover -s src/tests/unit`

### Integration tests
1. Set up environment variables locally:
    - `TEST_COSMOS_DB_ACCOUNT_HOST=https://{Cosmos-DB-account-name}.documents.azure.com:443/`
    - `TEST_COSMOS_DB_ACCOUNT_KEY={key}`
    - `TEST_COSMOS_DB_DATABASE_ID=PlanteTest`
2. Create database and required tables by running `python src/migrations.py` with `EnvType.TEST`
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