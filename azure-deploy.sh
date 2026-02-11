#!/bin/bash

# Get the environment name from the first command line argument and convert it to lowercase
ENV_NAME=$(echo "$1" | tr '[:upper:]' '[:lower:]')
ENV_NAME_UPPER=$(echo "$1" | tr '[:lower:]' '[:upper:]')

LOCATION="germanywestcentral"
TEMPLATE_PATH="azure_infra/main.bicep"
RESOURCE_GROUP_NAME="receipt-parser-rg"

if [ "$ENV_NAME" = "test" ]; then
  RESOURCE_GROUP_NAME="plante-$ENV_NAME"
elif [ "$ENV_NAME" = "dev" ]; then
  RESOURCE_GROUP_NAME="plante-$ENV_NAME"
elif [ "$ENV_NAME" = "stage" ]; then
  RESOURCE_GROUP_NAME="plante-prod"
else
  echo "Unknown environment: $ENV_NAME"
  exit 1
fi

if [ "$ENV_NAME" = "stage" ]; then
  FUNCTION_APP_NAME="receipt-parser"
else
  FUNCTION_APP_NAME="receipt-parser-$ENV_NAME"
fi

echo "Deploying azure function to $RESOURCE_GROUP_NAME"

# Create new resource group (if does not exist)
az group create -l $LOCATION -n $RESOURCE_GROUP_NAME && \

# Deploy resources inside resource group
OUTPUTS=$(az deployment group create --mode Incremental \
  --resource-group $RESOURCE_GROUP_NAME \
  --template-file $TEMPLATE_PATH \
  --parameters envName="$ENV_NAME" functionAppName="$FUNCTION_APP_NAME" \
  --query properties.outputs) && \


if [[ "$ENV_NAME" = "test" || "$ENV_NAME" = "dev" ]]; then
  COSMOS_DB_ACCOUNT_HOST=$(echo "$OUTPUTS" | jq -r '.cosmosDbAccountHost.value') && \
  COSMOS_DB_ACCOUNT_KEY=$(echo "$OUTPUTS" | jq -r '.cosmosDbAccountKey.value') && \
  COSMOS_DB_DATABASE_ID=$(echo "$OUTPUTS" | jq -r '.cosmosDbDatabaseId.value') && \
  sed -i "" "s|${ENV_NAME_UPPER}_COSMOS_DB_ACCOUNT_HOST=.*$|${ENV_NAME_UPPER}_COSMOS_DB_ACCOUNT_HOST=$COSMOS_DB_ACCOUNT_HOST|g" .env && \
  sed -i "" "s|${ENV_NAME_UPPER}_COSMOS_DB_ACCOUNT_KEY=.*$|${ENV_NAME_UPPER}_COSMOS_DB_ACCOUNT_KEY=$COSMOS_DB_ACCOUNT_KEY|g" .env && \
  sed -i "" "s|${ENV_NAME_UPPER}_COSMOS_DB_DATABASE_ID=.*$|${ENV_NAME_UPPER}_COSMOS_DB_DATABASE_ID=$COSMOS_DB_DATABASE_ID|g" .env
fi && \

APPINSIGHTS_CONNECTION_STRING=$(echo "$OUTPUTS" | jq -r '.appInsightsConnectionString.value') && \

if [ "$ENV_NAME" = "dev" ]; then
  AZURE_WEB_JOBS_STORAGE=$(echo "$OUTPUTS" | jq -r '.azureWebJobsStorage.value') && \
  APPINSIGHTS_KEY=$(echo "$OUTPUTS" | jq -r '.appInsightsInstrumentationKey.value') && \

  jq --arg a "$AZURE_WEB_JOBS_STORAGE" --arg b "$APPINSIGHTS_KEY" \
  --arg c "$COSMOS_DB_ACCOUNT_HOST" --arg d "$COSMOS_DB_ACCOUNT_KEY" --arg e "$COSMOS_DB_DATABASE_ID" \
  '.Values.AzureWebJobsStorage = $a | .Values.APPINSIGHTS_INSTRUMENTATIONKEY = $b | .Values.DEV_COSMOS_DB_ACCOUNT_HOST = $c | .Values.DEV_COSMOS_DB_ACCOUNT_KEY = $d | .Values.DEV_COSMOS_DB_DATABASE_ID = $e | .Values.ENV_NAME = "dev"' \
  azure_functions/local.settings.json > temp.json && mv temp.json azure_functions/local.settings.json && \

  sed -i "" "s|APPLICATIONINSIGHTS_CONNECTION_STRING=.*$|APPLICATIONINSIGHTS_CONNECTION_STRING=\"$APPINSIGHTS_CONNECTION_STRING\"|g" .env
fi && \

source ./.env && \

# run db migrations
.venv/bin/python ./db_migration.py --env "$ENV_NAME" --appinsights "$APPINSIGHTS_CONNECTION_STRING" && \

# Deploy the azure function code
# Copy src directory to azure_functions for deployment
cp -r src azure_functions/ && \

# Generate requirements.txt in azure_functions
uv export --format requirements-txt --no-hashes > azure_functions/requirements.txt && \

cd azure_functions && \
if [ "$ENV_NAME" = "stage" ]; then
  # Create stage deployment slot
  az functionapp deployment slot create --name "$FUNCTION_APP_NAME" \
    --resource-group $RESOURCE_GROUP_NAME --slot stage

  func azure functionapp publish "$FUNCTION_APP_NAME" --python --build remote --slot "$ENV_NAME"
else
  func azure functionapp publish "$FUNCTION_APP_NAME" --python --build remote
fi && \
cd .. && \
rm -rf azure_functions/src azure_functions/requirements.txt
