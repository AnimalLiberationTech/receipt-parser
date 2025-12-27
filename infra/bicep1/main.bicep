param location string = resourceGroup().location

@description('Resource name prefix')
param resourceNamePrefix string
var envResourceNamePrefix = toLower(resourceNamePrefix)

@description('Deployment name (used as parent ID for child deployments)')
param deploymentNameId string = '0000000000'

@description('Name of the staging deployment slot')
var functionAppStagingSlot = 'staging'




/* ###################################################################### */
// Create app configuration to store settings
/* ###################################################################### */
resource azAppConfiguration 'Microsoft.AppConfiguration/configurationStores@2021-10-01-preview' = {
  name: '${envResourceNamePrefix}-appconfig'
  location: location
  sku: {
    name: 'Standard'
  }
}
// set two default values for APP_VERSION & COMMIT_HASH
resource appConfigKey_AppVersion 'Microsoft.AppConfiguration/configurationStores/keyValues@2021-10-01-preview' = {
  name: '${azAppConfiguration.name}/APP_VERSION'
  properties: {
    value: '0.0.0'
  }
}
resource appConfigKey_CommitHash 'Microsoft.AppConfiguration/configurationStores/keyValues@2021-10-01-preview' = {
  name: '${azAppConfiguration.name}/COMMIT_HASH'
  properties: {
    value: '0000000000000000000000000000000000000000'
  }
}




/* ###################################################################### */
// Create storage account for function app prereq
/* ###################################################################### */
resource azStorageAccount 'Microsoft.Storage/storageAccounts@2021-08-01' = {
  name: '${envResourceNamePrefix}storage'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
}
var azStorageAccountPrimaryAccessKey = listKeys(azStorageAccount.id, azStorageAccount.apiVersion).keys[0].value




/* ###################################################################### */
// Create Application Insights
/* ###################################################################### */
resource azAppInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${envResourceNamePrefix}-ai'
  location: location
  kind: 'web'
  properties:{
    Application_Type: 'web'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}
var azAppInsightsInstrumentationKey = azAppInsights.properties.InstrumentationKey



/* ###################################################################### */
// Create Function App (+Server Farm ASP)
//   - NOTE: set app settings later
/* ###################################################################### */
resource azHostingPlan 'Microsoft.Web/serverfarms@2021-03-01' = {
  name: '${envResourceNamePrefix}-asp'
  location: location
  kind: 'linux'
  sku: {
    name: 'S1'
  }
  properties: {
    reserved: true
  }
}

resource azFunctionApp 'Microsoft.Web/sites@2021-03-01' = {
  name: '${envResourceNamePrefix}-app'
  kind: 'functionapp'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    httpsOnly: true
    serverFarmId: azHostingPlan.id
    clientAffinityEnabled: true
    reserved: true
    siteConfig: {
      alwaysOn: true
      linuxFxVersion: 'Python|3.11'
    }
  }
}

/* ###################################################################### */
// Create Function App's staging slot for
//   - NOTE: set app settings later
/* ###################################################################### */
resource azFunctionSlotStaging 'Microsoft.Web/sites/slots@2021-03-01' = {
  name: '${azFunctionApp.name}/${functionAppStagingSlot}'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    enabled: true
    httpsOnly: true
  }
}




/* ###################################################################### */
// Configure & set app settings on function app's deployment slots
/* ###################################################################### */
// set specific app settings to be a slot specific values
resource functionSlotConfig 'Microsoft.Web/sites/config@2021-03-01' = {
  name: 'slotConfigNames'
  parent: azFunctionApp
  properties: {
    appSettingNames: [
      'APP_CONFIGURATION_LABEL'
    ]
  }
}

// set the app settings on function app's deployment slots
module appService_appSettings 'appservice-appsettings-config.bicep' = {
  name: '${deploymentNameId}-appservice-config'
  params: {
    appConfigurationName: azAppConfiguration.name
    appConfiguration_appConfigLabel_value_production: 'production'
    appConfiguration_appConfigLabel_value_staging: 'staging'
    applicationInsightsInstrumentationKey: azAppInsightsInstrumentationKey
    storageAccountName: azStorageAccount.name
    storageAccountAccessKey: azStorageAccountPrimaryAccessKey
    functionAppName: azFunctionApp.name
    functionAppStagingSlotName: azFunctionSlotStaging.name
  }
}




/* ###################################################################### */
// grant resource [AzureFunction MSI] READ permissions > resource [APP CONFIGURATION] */
/* ###################################################################### */
module grantAppServiceToAppConfig 'appservice-appconfig-grant.bicep' = {
  name: '${deploymentNameId}-grant-appService-appConfig'
  params: {
    azAppConfigurationId: azAppConfiguration.id
    azFunctionAppId: azFunctionApp.id
    azFunctionAppPrincipalId: azFunctionApp.identity.principalId
  }
}




/* define outputs */
output appConfigName string = azAppConfiguration.name
output appInsightsInstrumentionKey string = azAppInsightsInstrumentationKey
output functionAppName string = azFunctionApp.name
output functionAppSlotName string = functionAppStagingSlot
