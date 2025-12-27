



targetScope = 'subscription'

@description('The environment (dev, test, prod, ...')
@maxLength(4)
param environment string = 'dev'

param organizationName string = 'plante'
param applicationName string = 'receipt-parser'

@description('The Azure region where all resources in this example should be created')
param location string = 'West Europe'

@description('A list of tags to apply to the resources')
var defaultTags = {
  environment: environment
  application: applicationName
}

@description('An array of NameValues that needs to be added as environment variables')
var applicationEnvironmentVariables = [
// You can add your custom environment variables here
      {
        name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
        value: instrumentation.outputs.appInsightsInstrumentationKey
      }
]

resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: 'rg-${organizationName}'
  location: location
  tags: defaultTags
}

module instrumentation 'modules/app-insights.bicep' = {
  name: 'instrumentation'
  scope: resourceGroup(rg.name)
  params: {
    location: location
    applicationName: applicationName
    environment: environment
    resourceTags: defaultTags
  }
}

module function 'modules/function.bicep' = {
  name: 'function'
  scope: resourceGroup(rg.name)
  params: {
    location: location
    applicationName: applicationName
    environment: environment
    resourceTags: defaultTags
    environmentVariables: applicationEnvironmentVariables
  }
}

module cosmosdb 'modules/cosmosdb.bicep' = {
  name: 'cosmosdb'
  scope: resourceGroup(rg.name)
  params: {
    location: location
    applicationName: applicationName
    resourceTags: defaultTags
  }
}
