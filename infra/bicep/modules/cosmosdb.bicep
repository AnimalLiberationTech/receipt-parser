param organizationName string = 'plante'
param applicationName string = 'receipt-parser'
param location string = 'West Europe'
param resourceTags object = {}


resource cosmosDbAccount 'Microsoft.DocumentDB/databaseAccounts@2023-11-15' = {
  name: 'cosmosdb-${organizationName}'
  location: location
  kind: 'GlobalDocumentDB'
  tags: union(resourceTags, {
    defaultExperience: 'Core (SQL)'
    'hidden-cosmos-mmspecial': ''
  })
  properties: {
    analyticalStorageConfiguration: {
      schemaType: 'WellDefined'
    }
    backupPolicy: {
      type: 'Periodic'
      periodicModeProperties: {
        backupIntervalInMinutes: 240
        backupRetentionIntervalInHours: 8
        backupStorageRedundancy: 'Geo'
      }
    }
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
    capacity: {
      totalThroughputLimit: 4000
    }
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
      maxIntervalInSeconds: 5
      maxStalenessPrefix: 100
    }
    cors: []
    databaseAccountOfferType: 'Standard'
    defaultIdentity: 'FirstPartyIdentity'
    disableKeyBasedMetadataWriteAccess: false
    disableLocalAuth: false
    enableAnalyticalStorage: false
    enableAutomaticFailover: false
    enableBurstCapacity: false
    enableFreeTier: true
    enableMultipleWriteLocations: false
    enablePartitionMerge: false
    ipRules: []
    isVirtualNetworkFilterEnabled: false
    locations: [
      {
        failoverPriority: 0
        isZoneRedundant: false
        locationName: location
      }
    ]
    minimalTlsVersion: 'Tls12'
    networkAclBypass: 'None'
    networkAclBypassResourceIds: []
    publicNetworkAccess: 'Enabled'
    virtualNetworkRules: []
  }
  identity: {
    type: 'None'
  }
}

resource cosmosDbDev 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-11-15' = {
  parent: cosmosDbAccount
  name: '${applicationName}-dev'
  properties: {
    resource: {
      id: '${applicationName}-dev'
    }
  }
}

resource cosmosDbDevProductBarcode 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-11-15' = {
  parent: cosmosDbDev
  name: 'product_barcode'
  properties: {
    resource: {
      conflictResolutionPolicy: {
        conflictResolutionPath: '/_ts'
        mode: 'LastWriterWins'
      }
      id: 'product_barcode'
      indexingPolicy: {
        automatic: true
        excludedPaths: [
          {
            path: '/"_etag"/?'
          }
        ]
        includedPaths: [
          {
            path: '/*'
          }
        ]
        indexingMode: 'consistent'
      }
      partitionKey: {
        kind: 'Hash'
        paths: [
          '/shop_id'
        ]
        version: 2
      }
    }
  }
  dependsOn: [
  ]
}

resource cosmosDbDevPurchase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-11-15' = {
  parent: cosmosDbDev
  name: 'purchase-dev'
  properties: {
    resource: {
      conflictResolutionPolicy: {
        conflictResolutionPath: '/_ts'
        mode: 'LastWriterWins'
      }
      id: 'purchase-dev'
      indexingPolicy: {
        automatic: true
        excludedPaths: [
          {
            path: '/"_etag"/?'
          }
        ]
        includedPaths: [
          {
            path: '/*'
          }
        ]
        indexingMode: 'consistent'
      }
      partitionKey: {
        kind: 'Hash'
        paths: [
          '/shop_id'
        ]
        version: 2
      }
    }
  }
  dependsOn: [
  ]
}

resource cosmosDbDevReceipt 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-11-15' = {
  parent: cosmosDbDev
  name: 'receipt'
  properties: {
    resource: {
      conflictResolutionPolicy: {
        conflictResolutionPath: '/_ts'
        mode: 'LastWriterWins'
      }
      id: 'receipt'
      indexingPolicy: {
        automatic: true
        excludedPaths: [
          {
            path: '/"_etag"/?'
          }
        ]
        includedPaths: [
          {
            path: '/*'
          }
        ]
        indexingMode: 'consistent'
      }
      partitionKey: {
        kind: 'Hash'
        paths: [
          '/user_id'
        ]
        version: 2
      }
    }
  }
  dependsOn: [
  ]
}

resource cosmosDbDevShop 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-11-15' = {
  parent: cosmosDbDev
  name: 'shop'
  properties: {
    resource: {
      conflictResolutionPolicy: {
        conflictResolutionPath: '/_ts'
        mode: 'LastWriterWins'
      }
      id: 'shop'
      indexingPolicy: {
        automatic: true
        excludedPaths: [
          {
            path: '/"_etag"/?'
          }
        ]
        includedPaths: [
          {
            path: '/*'
          }
        ]
        indexingMode: 'consistent'
      }
      partitionKey: {
        kind: 'Hash'
        paths: [
          '/country_code'
        ]
        version: 2
      }
    }
  }
  dependsOn: [
  ]
}
