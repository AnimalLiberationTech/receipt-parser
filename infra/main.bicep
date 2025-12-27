@description('Environment name')
param envName string

@description('Azure function name')
param functionAppName string

@description('Location for all resources.')
param location string = resourceGroup().location

param tags object = {}
param appInsightsRetention int = 30

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: '${toLower(replace(resourceGroup().name, '-', ''))}storage'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: true
    minimumTlsVersion: 'TLS1_2'
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${resourceGroup().name}-insights'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Flow_Type: 'Bluefield'
    Request_Source: 'rest'
    RetentionInDays: appInsightsRetention
  }
  tags: tags
}

resource databaseAccounts 'Microsoft.DocumentDB/databaseAccounts@2024-02-15-preview' = {
  name: '${resourceGroup().name}-cosmos-db'
  location: location
  tags: {
    defaultExperience: 'Core (SQL)'
    'hidden-cosmos-mmspecial': ''
  }
  kind: 'GlobalDocumentDB'
  identity: {
    type: 'None'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
    enableAutomaticFailover: false
    enableMultipleWriteLocations: false
    isVirtualNetworkFilterEnabled: false
    virtualNetworkRules: []
    disableKeyBasedMetadataWriteAccess: false
    enableFreeTier: false
    enableAnalyticalStorage: false
    analyticalStorageConfiguration: {
      schemaType: 'WellDefined'
    }
    databaseAccountOfferType: 'Standard'
    enableMaterializedViews: false
    defaultIdentity: 'FirstPartyIdentity'
    networkAclBypass: 'None'
    disableLocalAuth: false
    enablePartitionMerge: false
    enablePerRegionPerPartitionAutoscale: false
    enableBurstCapacity: false
    minimalTlsVersion: 'Tls12'
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
      maxIntervalInSeconds: 5
      maxStalenessPrefix: 100
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    cors: [
      {
        allowedOrigins: '*'
      }
    ]
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
    ipRules: []
    backupPolicy: {
      type: 'Periodic'
      periodicModeProperties: {
        backupIntervalInMinutes: 240
        backupRetentionIntervalInHours: 8
        backupStorageRedundancy: 'Geo'
      }
    }
    networkAclBypassResourceIds: []
    diagnosticLogSettings: {
      enableFullTextQuery: 'None'
    }
    capacity: {
      totalThroughputLimit: 4000
    }
  }
  resource cosmosDbDatabase 'sqlDatabases' = {
    name: '${resourceGroup().name}-db'
    properties: {
      resource: {
        id: '${resourceGroup().name}-db'
      }
    }
  }
}

resource serverFarm 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: '${resourceGroup().name}-asp'
  location: location
  tags: tags
  sku: {
    name: 'Y1'
    tier: 'Standard'
  }
  properties: {
    reserved: true
  }
  kind: 'linux'
}

resource functionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: functionAppName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  kind: 'functionapp'
  properties: {
    enabled: true
    serverFarmId: resourceId('Microsoft.Web/serverfarms', serverFarm.name)
    httpsOnly: true
    siteConfig: {
      cors: {
        allowedOrigins: [
          '*'
        ]
      }
      pythonVersion: '3.12'
      linuxFxVersion: 'python|3.12'
      numberOfWorkers: 1
      alwaysOn: false
      functionAppScaleLimit: 200
      minimumElasticInstanceCount: 0
      minTlsVersion: '1.2'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'  // required
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${listKeys(resourceId('Microsoft.Storage/storageAccounts', storageAccount.name), '2021-08-01').keys[0].value};EndpointSuffix=core.windows.net'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'  // required for consumption plan functions
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${listKeys(resourceId('Microsoft.Storage/storageAccounts', storageAccount.name), '2019-04-01').keys[0].value};EndpointSuffix=core.windows.net'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'  // required for consumption plan functions
          value: replace(toLower(functionAppName), '-', '')
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'  // required
          value: 'true'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: reference('Microsoft.Insights/components/${appInsights.name}', '2015-05-01').InstrumentationKey
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: reference('Microsoft.Insights/components/${appInsights.name}', '2015-05-01').ConnectionString
        }
        {
          name: 'AzureWebJobsFeatureFlags'
          value: 'EnableWorkerIndexing'
        }
        {
          name: 'ApplicationInsightsAgent_EXTENSION_VERSION'
          value: '~2'
        }
        {
          name: 'InstrumentationEngine_EXTENSION_VERSION'
          value: '~1'
        }
        {
          name: 'AzureWebJobsSecretStorageType'
          value: 'Blob'
        }
        {
          name: 'APP_HOST'
          value: 'https://${functionAppName}.azurewebsites.net/'
        }
        {
          name: '${toUpper(envName)}_COSMOS_DB_ACCOUNT_HOST'
          value: databaseAccounts.properties.documentEndpoint
        }
        {
          name: '${toUpper(envName)}_COSMOS_DB_ACCOUNT_KEY'
          value: databaseAccounts.listKeys().primaryMasterKey
        }
        {
          name: '${toUpper(envName)}_COSMOS_DB_DATABASE_ID'
          value: '${resourceGroup().name}-db'
        }
        {
          name: 'ENV_NAME'
          value: envName
        }
      ]
    }
  }
}

#disable-next-line outputs-should-not-contain-secrets
output azureWebJobsStorage string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${listKeys(resourceId('Microsoft.Storage/storageAccounts', storageAccount.name), '2021-08-01').keys[0].value};EndpointSuffix=core.windows.net'
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output appInsightsConnectionString string = appInsights.properties.ConnectionString
output cosmosDbAccountHost string = databaseAccounts.properties.documentEndpoint
#disable-next-line outputs-should-not-contain-secrets
output cosmosDbAccountKey string = databaseAccounts.listKeys().primaryMasterKey
output cosmosDbDatabaseId string = '${resourceGroup().name}-db'
