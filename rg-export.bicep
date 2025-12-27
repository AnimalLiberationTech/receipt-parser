param actionGroups_Application_Insights_Smart_Detection_name string
param components_plante_receipt_parser_name string
param databaseAccounts_plante_name string
param serverfarms_ASP_plante_8c1e_name string
param sites_plante_receipt_parser_name string
param smartdetectoralertrules_failure_anomalies_plante_receipt_parser_name string
param storageAccounts_plante_name string
param workspaces_DefaultWorkspace_8ddcb118_f248_49f7_b954_611e1c7ffad2_WEU_externalid string

resource databaseAccounts_plante_name_resource 'Microsoft.DocumentDB/databaseAccounts@2023-11-15' = {
  identity: {
    type: 'None'
  }
  kind: 'GlobalDocumentDB'
  location: 'West Europe'
  name: databaseAccounts_plante_name
  properties: {
    analyticalStorageConfiguration: {
      schemaType: 'WellDefined'
    }
    backupPolicy: {
      periodicModeProperties: {
        backupIntervalInMinutes: 240
        backupRetentionIntervalInHours: 8
        backupStorageRedundancy: 'Geo'
      }
      type: 'Periodic'
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
    enableFreeTier: false
    enableMultipleWriteLocations: false
    enablePartitionMerge: false
    ipRules: []
    isVirtualNetworkFilterEnabled: false
    keysMetadata: {}
    locations: [
      {
        failoverPriority: 0
        isZoneRedundant: false
        locationName: 'West Europe'
        provisioningState: 'Succeeded'
      }
    ]
    minimalTlsVersion: 'Tls12'
    networkAclBypass: 'None'
    networkAclBypassResourceIds: []
    publicNetworkAccess: 'Enabled'
    virtualNetworkRules: []
  }
  tags: {
    defaultExperience: 'Core (SQL)'
    'hidden-cosmos-mmspecial': ''
  }
}

resource actionGroups_Application_Insights_Smart_Detection_name_resource 'microsoft.insights/actionGroups@2023-01-01' = {
  location: 'Global'
  name: actionGroups_Application_Insights_Smart_Detection_name
  properties: {
    armRoleReceivers: [
      {
        name: 'Monitoring Contributor'
        roleId: '749f88d5-cbae-40b8-bcfc-e573ddc772fa'
        useCommonAlertSchema: true
      }
      {
        name: 'Monitoring Reader'
        roleId: '43d0d8ad-25c7-4714-9337-8ba259a9fe05'
        useCommonAlertSchema: true
      }
    ]
    automationRunbookReceivers: []
    azureAppPushReceivers: []
    azureFunctionReceivers: []
    emailReceivers: []
    enabled: true
    eventHubReceivers: []
    groupShortName: 'SmartDetect'
    itsmReceivers: []
    logicAppReceivers: []
    smsReceivers: []
    voiceReceivers: []
    webhookReceivers: []
  }
}

resource components_plante_receipt_parser_name_resource 'microsoft.insights/components@2020-02-02' = {
  kind: 'web'
  location: 'westeurope'
  name: components_plante_receipt_parser_name
  properties: {
    Application_Type: 'web'
    Flow_Type: 'Redfield'
    IngestionMode: 'LogAnalytics'
    Request_Source: 'IbizaWebAppExtensionCreate'
    RetentionInDays: 90
    WorkspaceResourceId: workspaces_DefaultWorkspace_8ddcb118_f248_49f7_b954_611e1c7ffad2_WEU_externalid
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

resource storageAccounts_plante_name_resource 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  kind: 'Storage'
  location: 'westeurope'
  name: storageAccounts_plante_name
  properties: {
    allowBlobPublicAccess: false
    allowCrossTenantReplication: false
    defaultToOAuthAuthentication: true
    encryption: {
      keySource: 'Microsoft.Storage'
      services: {
        blob: {
          enabled: true
          keyType: 'Account'
        }
        file: {
          enabled: true
          keyType: 'Account'
        }
      }
    }
    minimumTlsVersion: 'TLS1_2'
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
      ipRules: []
      virtualNetworkRules: []
    }
    supportsHttpsTrafficOnly: true
  }
  sku: {
    name: 'Standard_LRS'
    tier: 'Standard'
  }
}

resource serverfarms_ASP_plante_8c1e_name_resource 'Microsoft.Web/serverfarms@2023-01-01' = {
  kind: 'functionapp'
  location: 'West Europe'
  name: serverfarms_ASP_plante_8c1e_name
  properties: {
    elasticScaleEnabled: false
    hyperV: false
    isSpot: false
    isXenon: false
    maximumElasticWorkerCount: 1
    perSiteScaling: false
    reserved: true
    targetWorkerCount: 0
    targetWorkerSizeId: 0
    zoneRedundant: false
  }
  sku: {
    capacity: 0
    family: 'Y'
    name: 'Y1'
    size: 'Y1'
    tier: 'Dynamic'
  }
}

resource databaseAccounts_plante_name_databaseAccounts_plante_name_Dev 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-11-15' = {
  parent: databaseAccounts_plante_name_resource
  name: '${databaseAccounts_plante_name}Dev'
  properties: {
    resource: {
      id: 'PlanteDev'
    }
  }
}

resource databaseAccounts_plante_name_00000000_0000_0000_0000_000000000001 'Microsoft.DocumentDB/databaseAccounts/sqlRoleDefinitions@2023-11-15' = {
  parent: databaseAccounts_plante_name_resource
  name: '00000000-0000-0000-0000-000000000001'
  properties: {
    assignableScopes: [
      databaseAccounts_plante_name_resource.id
    ]
    permissions: [
      {
        dataActions: [
          'Microsoft.DocumentDB/databaseAccounts/readMetadata'
          'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/executeQuery'
          'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/readChangeFeed'
          'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/read'
        ]
        notDataActions: []
      }
    ]
    roleName: 'Cosmos DB Built-in Data Reader'
    type: 'BuiltInRole'
  }
}

resource databaseAccounts_plante_name_00000000_0000_0000_0000_000000000002 'Microsoft.DocumentDB/databaseAccounts/sqlRoleDefinitions@2023-11-15' = {
  parent: databaseAccounts_plante_name_resource
  name: '00000000-0000-0000-0000-000000000002'
  properties: {
    assignableScopes: [
      databaseAccounts_plante_name_resource.id
    ]
    permissions: [
      {
        dataActions: [
          'Microsoft.DocumentDB/databaseAccounts/readMetadata'
          'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/*'
          'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/*'
        ]
        notDataActions: []
      }
    ]
    roleName: 'Cosmos DB Built-in Data Contributor'
    type: 'BuiltInRole'
  }
}

resource databaseAccounts_plante_name_databaseAccounts_plante_name_Dev_product_barcode 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-11-15' = {
  parent: databaseAccounts_plante_name_databaseAccounts_plante_name_Dev
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

    databaseAccounts_plante_name_resource
  ]
}

resource databaseAccounts_plante_name_databaseAccounts_plante_name_Dev_purchase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-11-15' = {
  parent: databaseAccounts_plante_name_databaseAccounts_plante_name_Dev
  name: 'purchase'
  properties: {
    resource: {
      conflictResolutionPolicy: {
        conflictResolutionPath: '/_ts'
        mode: 'LastWriterWins'
      }
      id: 'purchase'
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

    databaseAccounts_plante_name_resource
  ]
}

resource databaseAccounts_plante_name_databaseAccounts_plante_name_Dev_receipt 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-11-15' = {
  parent: databaseAccounts_plante_name_databaseAccounts_plante_name_Dev
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

    databaseAccounts_plante_name_resource
  ]
}

resource databaseAccounts_plante_name_databaseAccounts_plante_name_Dev_shop 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-11-15' = {
  parent: databaseAccounts_plante_name_databaseAccounts_plante_name_Dev
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

    databaseAccounts_plante_name_resource
  ]
}







resource components_plante_receipt_parser_name_degradationindependencyduration 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_plante_receipt_parser_name_resource
  location: 'westeurope'
  name: 'degradationindependencyduration'
  properties: {
    CustomEmails: []
    Enabled: true
    RuleDefinitions: {
      Description: 'Smart Detection rules notify you of performance anomaly issues.'
      DisplayName: 'Degradation in dependency duration'
      HelpUrl: 'https://docs.microsoft.com/en-us/azure/application-insights/app-insights-proactive-performance-diagnostics'
      IsEnabledByDefault: true
      IsHidden: false
      IsInPreview: false
      Name: 'degradationindependencyduration'
      SupportsEmailNotifications: true
    }
    SendEmailsToSubscriptionOwners: true
  }
}

resource components_plante_receipt_parser_name_degradationinserverresponsetime 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_plante_receipt_parser_name_resource
  location: 'westeurope'
  name: 'degradationinserverresponsetime'
  properties: {
    CustomEmails: []
    Enabled: true
    RuleDefinitions: {
      Description: 'Smart Detection rules notify you of performance anomaly issues.'
      DisplayName: 'Degradation in server response time'
      HelpUrl: 'https://docs.microsoft.com/en-us/azure/application-insights/app-insights-proactive-performance-diagnostics'
      IsEnabledByDefault: true
      IsHidden: false
      IsInPreview: false
      Name: 'degradationinserverresponsetime'
      SupportsEmailNotifications: true
    }
    SendEmailsToSubscriptionOwners: true
  }
}

resource components_plante_receipt_parser_name_digestMailConfiguration 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_plante_receipt_parser_name_resource
  location: 'westeurope'
  name: 'digestMailConfiguration'
  properties: {
    CustomEmails: []
    Enabled: true
    RuleDefinitions: {
      Description: 'This rule describes the digest mail preferences'
      DisplayName: 'Digest Mail Configuration'
      HelpUrl: 'www.homail.com'
      IsEnabledByDefault: true
      IsHidden: true
      IsInPreview: false
      Name: 'digestMailConfiguration'
      SupportsEmailNotifications: true
    }
    SendEmailsToSubscriptionOwners: true
  }
}

resource components_plante_receipt_parser_name_extension_billingdatavolumedailyspikeextension 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_plante_receipt_parser_name_resource
  location: 'westeurope'
  name: 'extension_billingdatavolumedailyspikeextension'
  properties: {
    CustomEmails: []
    Enabled: true
    RuleDefinitions: {
      Description: 'This detection rule automatically analyzes the billing data generated by your application, and can warn you about an unusual increase in your application\'s billing costs'
      DisplayName: 'Abnormal rise in daily data volume (preview)'
      HelpUrl: 'https://github.com/Microsoft/ApplicationInsights-Home/tree/master/SmartDetection/billing-data-volume-daily-spike.md'
      IsEnabledByDefault: true
      IsHidden: false
      IsInPreview: true
      Name: 'extension_billingdatavolumedailyspikeextension'
      SupportsEmailNotifications: false
    }
    SendEmailsToSubscriptionOwners: true
  }
}

resource components_plante_receipt_parser_name_extension_canaryextension 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_plante_receipt_parser_name_resource
  location: 'westeurope'
  name: 'extension_canaryextension'
  properties: {
    CustomEmails: []
    Enabled: true
    RuleDefinitions: {
      Description: 'Canary extension'
      DisplayName: 'Canary extension'
      HelpUrl: 'https://github.com/Microsoft/ApplicationInsights-Home/blob/master/SmartDetection/'
      IsEnabledByDefault: true
      IsHidden: true
      IsInPreview: true
      Name: 'extension_canaryextension'
      SupportsEmailNotifications: false
    }
    SendEmailsToSubscriptionOwners: true
  }
}

resource components_plante_receipt_parser_name_extension_exceptionchangeextension 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_plante_receipt_parser_name_resource
  location: 'westeurope'
  name: 'extension_exceptionchangeextension'
  properties: {
    CustomEmails: []
    Enabled: true
    RuleDefinitions: {
      Description: 'This detection rule automatically analyzes the exceptions thrown in your application, and can warn you about unusual patterns in your exception telemetry.'
      DisplayName: 'Abnormal rise in exception volume (preview)'
      HelpUrl: 'https://github.com/Microsoft/ApplicationInsights-Home/blob/master/SmartDetection/abnormal-rise-in-exception-volume.md'
      IsEnabledByDefault: true
      IsHidden: false
      IsInPreview: true
      Name: 'extension_exceptionchangeextension'
      SupportsEmailNotifications: false
    }
    SendEmailsToSubscriptionOwners: true
  }
}

resource components_plante_receipt_parser_name_extension_memoryleakextension 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_plante_receipt_parser_name_resource
  location: 'westeurope'
  name: 'extension_memoryleakextension'
  properties: {
    CustomEmails: []
    Enabled: true
    RuleDefinitions: {
      Description: 'This detection rule automatically analyzes the memory consumption of each process in your application, and can warn you about potential memory leaks or increased memory consumption.'
      DisplayName: 'Potential memory leak detected (preview)'
      HelpUrl: 'https://github.com/Microsoft/ApplicationInsights-Home/tree/master/SmartDetection/memory-leak.md'
      IsEnabledByDefault: true
      IsHidden: false
      IsInPreview: true
      Name: 'extension_memoryleakextension'
      SupportsEmailNotifications: false
    }
    SendEmailsToSubscriptionOwners: true
  }
}

resource components_plante_receipt_parser_name_extension_securityextensionspackage 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_plante_receipt_parser_name_resource
  location: 'westeurope'
  name: 'extension_securityextensionspackage'
  properties: {
    CustomEmails: []
    Enabled: true
    RuleDefinitions: {
      Description: 'This detection rule automatically analyzes the telemetry generated by your application and detects potential security issues.'
      DisplayName: 'Potential security issue detected (preview)'
      HelpUrl: 'https://github.com/Microsoft/ApplicationInsights-Home/blob/master/SmartDetection/application-security-detection-pack.md'
      IsEnabledByDefault: true
      IsHidden: false
      IsInPreview: true
      Name: 'extension_securityextensionspackage'
      SupportsEmailNotifications: false
    }
    SendEmailsToSubscriptionOwners: true
  }
}

resource components_plante_receipt_parser_name_extension_traceseveritydetector 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_plante_receipt_parser_name_resource
  location: 'westeurope'
  name: 'extension_traceseveritydetector'
  properties: {
    CustomEmails: []
    Enabled: true
    RuleDefinitions: {
      Description: 'This detection rule automatically analyzes the trace logs emitted from your application, and can warn you about unusual patterns in the severity of your trace telemetry.'
      DisplayName: 'Degradation in trace severity ratio (preview)'
      HelpUrl: 'https://github.com/Microsoft/ApplicationInsights-Home/blob/master/SmartDetection/degradation-in-trace-severity-ratio.md'
      IsEnabledByDefault: true
      IsHidden: false
      IsInPreview: true
      Name: 'extension_traceseveritydetector'
      SupportsEmailNotifications: false
    }
    SendEmailsToSubscriptionOwners: true
  }
}

resource components_plante_receipt_parser_name_longdependencyduration 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_plante_receipt_parser_name_resource
  location: 'westeurope'
  name: 'longdependencyduration'
  properties: {
    CustomEmails: []
    Enabled: true
    RuleDefinitions: {
      Description: 'Smart Detection rules notify you of performance anomaly issues.'
      DisplayName: 'Long dependency duration'
      HelpUrl: 'https://docs.microsoft.com/en-us/azure/application-insights/app-insights-proactive-performance-diagnostics'
      IsEnabledByDefault: true
      IsHidden: false
      IsInPreview: false
      Name: 'longdependencyduration'
      SupportsEmailNotifications: true
    }
    SendEmailsToSubscriptionOwners: true
  }
}

resource components_plante_receipt_parser_name_migrationToAlertRulesCompleted 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_plante_receipt_parser_name_resource
  location: 'westeurope'
  name: 'migrationToAlertRulesCompleted'
  properties: {
    CustomEmails: []
    Enabled: false
    RuleDefinitions: {
      Description: 'A configuration that controls the migration state of Smart Detection to Smart Alerts'
      DisplayName: 'Migration To Alert Rules Completed'
      HelpUrl: 'https://docs.microsoft.com/en-us/azure/application-insights/app-insights-proactive-performance-diagnostics'
      IsEnabledByDefault: false
      IsHidden: true
      IsInPreview: true
      Name: 'migrationToAlertRulesCompleted'
      SupportsEmailNotifications: false
    }
    SendEmailsToSubscriptionOwners: true
  }
}

resource components_plante_receipt_parser_name_slowpageloadtime 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_plante_receipt_parser_name_resource
  location: 'westeurope'
  name: 'slowpageloadtime'
  properties: {
    CustomEmails: []
    Enabled: true
    RuleDefinitions: {
      Description: 'Smart Detection rules notify you of performance anomaly issues.'
      DisplayName: 'Slow page load time'
      HelpUrl: 'https://docs.microsoft.com/en-us/azure/application-insights/app-insights-proactive-performance-diagnostics'
      IsEnabledByDefault: true
      IsHidden: false
      IsInPreview: false
      Name: 'slowpageloadtime'
      SupportsEmailNotifications: true
    }
    SendEmailsToSubscriptionOwners: true
  }
}

resource components_plante_receipt_parser_name_slowserverresponsetime 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_plante_receipt_parser_name_resource
  location: 'westeurope'
  name: 'slowserverresponsetime'
  properties: {
    CustomEmails: []
    Enabled: true
    RuleDefinitions: {
      Description: 'Smart Detection rules notify you of performance anomaly issues.'
      DisplayName: 'Slow server response time'
      HelpUrl: 'https://docs.microsoft.com/en-us/azure/application-insights/app-insights-proactive-performance-diagnostics'
      IsEnabledByDefault: true
      IsHidden: false
      IsInPreview: false
      Name: 'slowserverresponsetime'
      SupportsEmailNotifications: true
    }
    SendEmailsToSubscriptionOwners: true
  }
}




resource storageAccounts_plante_name_default 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccounts_plante_name_resource
  name: 'default'
  properties: {
    cors: {
      corsRules: []
    }
    deleteRetentionPolicy: {
      allowPermanentDelete: false
      enabled: false
    }
  }
  sku: {
    name: 'Standard_LRS'
    tier: 'Standard'
  }
}

resource Microsoft_Storage_storageAccounts_fileServices_storageAccounts_plante_name_default 'Microsoft.Storage/storageAccounts/fileServices@2023-01-01' = {
  parent: storageAccounts_plante_name_resource
  name: 'default'
  properties: {
    cors: {
      corsRules: []
    }
    protocolSettings: {
      smb: {}
    }
    shareDeleteRetentionPolicy: {
      days: 7
      enabled: true
    }
  }
  sku: {
    name: 'Standard_LRS'
    tier: 'Standard'
  }
}

resource Microsoft_Storage_storageAccounts_queueServices_storageAccounts_plante_name_default 'Microsoft.Storage/storageAccounts/queueServices@2023-01-01' = {
  parent: storageAccounts_plante_name_resource
  name: 'default'
  properties: {
    cors: {
      corsRules: []
    }
  }
}

resource Microsoft_Storage_storageAccounts_tableServices_storageAccounts_plante_name_default 'Microsoft.Storage/storageAccounts/tableServices@2023-01-01' = {
  parent: storageAccounts_plante_name_resource
  name: 'default'
  properties: {
    cors: {
      corsRules: []
    }
  }
}




resource sites_plante_receipt_parser_name_resource 'Microsoft.Web/sites@2023-01-01' = {
  kind: 'functionapp,linux'
  location: 'West Europe'
  name: sites_plante_receipt_parser_name
  properties: {
    clientAffinityEnabled: false
    clientCertEnabled: false
    clientCertMode: 'Required'
    containerSize: 1536
    customDomainVerificationId: '38B633B0825EE27750BEBDC15483CAB70E32BC0C11B7F9BF74D131E1E1A22B78'
    dailyMemoryTimeQuota: 0
    enabled: true
    hostNameSslStates: [
      {
        hostType: 'Standard'
        name: '${sites_plante_receipt_parser_name}.azurewebsites.net'
        sslState: 'Disabled'
      }
      {
        hostType: 'Repository'
        name: '${sites_plante_receipt_parser_name}.scm.azurewebsites.net'
        sslState: 'Disabled'
      }
    ]
    hostNamesDisabled: false
    httpsOnly: true
    hyperV: false
    isXenon: false
    keyVaultReferenceIdentity: 'SystemAssigned'
    publicNetworkAccess: 'Enabled'
    redundancyMode: 'None'
    reserved: true
    scmSiteAlsoStopped: false
    serverFarmId: serverfarms_ASP_plante_8c1e_name_resource.id
    siteConfig: {
      acrUseManagedIdentityCreds: false
      alwaysOn: false
      functionAppScaleLimit: 200
      http20Enabled: false
      linuxFxVersion: 'PYTHON|3.11'
      minimumElasticInstanceCount: 0
      numberOfWorkers: 1
    }
    storageAccountRequired: false
    vnetContentShareEnabled: false
    vnetImagePullEnabled: false
    vnetRouteAllEnabled: false
  }
  tags: {
    'hidden-link: /app-insights-conn-string': 'InstrumentationKey=e76995d2-f14c-44bc-a882-2145e36a8d11;IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/;LiveEndpoint=https://westeurope.livediagnostics.monitor.azure.com/'
    'hidden-link: /app-insights-instrumentation-key': 'e76995d2-f14c-44bc-a882-2145e36a8d11'
    'hidden-link: /app-insights-resource-id': '/subscriptions/8ddcb118-f248-49f7-b954-611e1c7ffad2/resourceGroups/plante/providers/microsoft.insights/components/plante-receipt-parser'
  }
}

resource sites_plante_receipt_parser_name_ftp 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2023-01-01' = {
  parent: sites_plante_receipt_parser_name_resource
  location: 'West Europe'
  name: 'ftp'
  properties: {
    allow: true
  }
  tags: {
    'hidden-link: /app-insights-conn-string': 'InstrumentationKey=e76995d2-f14c-44bc-a882-2145e36a8d11;IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/;LiveEndpoint=https://westeurope.livediagnostics.monitor.azure.com/'
    'hidden-link: /app-insights-instrumentation-key': 'e76995d2-f14c-44bc-a882-2145e36a8d11'
    'hidden-link: /app-insights-resource-id': '/subscriptions/8ddcb118-f248-49f7-b954-611e1c7ffad2/resourceGroups/plante/providers/microsoft.insights/components/plante-receipt-parser'
  }
}

resource sites_plante_receipt_parser_name_scm 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2023-01-01' = {
  parent: sites_plante_receipt_parser_name_resource
  location: 'West Europe'
  name: 'scm'
  properties: {
    allow: true
  }
  tags: {
    'hidden-link: /app-insights-conn-string': 'InstrumentationKey=e76995d2-f14c-44bc-a882-2145e36a8d11;IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/;LiveEndpoint=https://westeurope.livediagnostics.monitor.azure.com/'
    'hidden-link: /app-insights-instrumentation-key': 'e76995d2-f14c-44bc-a882-2145e36a8d11'
    'hidden-link: /app-insights-resource-id': '/subscriptions/8ddcb118-f248-49f7-b954-611e1c7ffad2/resourceGroups/plante/providers/microsoft.insights/components/plante-receipt-parser'
  }
}

resource sites_plante_receipt_parser_name_web 'Microsoft.Web/sites/config@2023-01-01' = {
  parent: sites_plante_receipt_parser_name_resource
  location: 'West Europe'
  name: 'web'
  properties: {
    acrUseManagedIdentityCreds: false
    alwaysOn: false
    autoHealEnabled: false
    azureStorageAccounts: {}
    cors: {
      allowedOrigins: [
        'https://portal.azure.com'
      ]
      supportCredentials: false
    }
    defaultDocuments: [
      'Default.htm'
      'Default.html'
      'Default.asp'
      'index.htm'
      'index.html'
      'iisstart.htm'
      'default.aspx'
      'index.php'
    ]
    detailedErrorLoggingEnabled: false
    experiments: {
      rampUpRules: []
    }
    ftpsState: 'FtpsOnly'
    functionAppScaleLimit: 200
    functionsRuntimeScaleMonitoringEnabled: false
    http20Enabled: false
    httpLoggingEnabled: false
    ipSecurityRestrictions: [
      {
        action: 'Allow'
        description: 'Allow all access'
        ipAddress: 'Any'
        name: 'Allow all'
        priority: 2147483647
      }
    ]
    linuxFxVersion: 'PYTHON|3.11'
    loadBalancing: 'LeastRequests'
    localMySqlEnabled: false
    logsDirectorySizeLimit: 35
    managedPipelineMode: 'Integrated'
    minTlsVersion: '1.2'
    minimumElasticInstanceCount: 0
    netFrameworkVersion: 'v4.0'
    numberOfWorkers: 1
    preWarmedInstanceCount: 0
    publicNetworkAccess: 'Enabled'
    publishingUsername: '$plante-receipt-parser'
    remoteDebuggingEnabled: false
    remoteDebuggingVersion: 'VS2019'
    requestTracingEnabled: false
    scmIpSecurityRestrictions: [
      {
        action: 'Allow'
        description: 'Allow all access'
        ipAddress: 'Any'
        name: 'Allow all'
        priority: 2147483647
      }
    ]
    scmIpSecurityRestrictionsUseMain: false
    scmMinTlsVersion: '1.2'
    scmType: 'None'
    use32BitWorkerProcess: false
    virtualApplications: [
      {
        physicalPath: 'site\\wwwroot'
        preloadEnabled: false
        virtualPath: '/'
      }
    ]
    vnetPrivatePortsCount: 0
    vnetRouteAllEnabled: false
    webSocketsEnabled: false
  }
  tags: {
    'hidden-link: /app-insights-conn-string': 'InstrumentationKey=e76995d2-f14c-44bc-a882-2145e36a8d11;IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/;LiveEndpoint=https://westeurope.livediagnostics.monitor.azure.com/'
    'hidden-link: /app-insights-instrumentation-key': 'e76995d2-f14c-44bc-a882-2145e36a8d11'
    'hidden-link: /app-insights-resource-id': '/subscriptions/8ddcb118-f248-49f7-b954-611e1c7ffad2/resourceGroups/plante/providers/microsoft.insights/components/plante-receipt-parser'
  }
}

resource sites_plante_receipt_parser_name_home 'Microsoft.Web/sites/functions@2023-01-01' = {
  parent: sites_plante_receipt_parser_name_resource
  location: 'West Europe'
  name: 'home'
  properties: {
    config: {}
    href: 'https://plante-receipt-parser.azurewebsites.net/admin/functions/home'
    invoke_url_template: 'https://plante-receipt-parser.azurewebsites.net/api/home'
    isDisabled: false
    language: 'python'
    script_href: 'https://plante-receipt-parser.azurewebsites.net/admin/vfs/home/site/wwwroot/function_app.py'
    test_data_href: 'https://plante-receipt-parser.azurewebsites.net/admin/vfs/tmp/FunctionsData/home.dat'
  }
}

resource sites_plante_receipt_parser_name_parse_from_url 'Microsoft.Web/sites/functions@2023-01-01' = {
  parent: sites_plante_receipt_parser_name_resource
  location: 'West Europe'
  name: 'parse_from_url'
  properties: {
    config: {}
    href: 'https://plante-receipt-parser.azurewebsites.net/admin/functions/parse_from_url'
    invoke_url_template: 'https://plante-receipt-parser.azurewebsites.net/api/parse-from-url'
    isDisabled: false
    language: 'python'
    script_href: 'https://plante-receipt-parser.azurewebsites.net/admin/vfs/home/site/wwwroot/function_app.py'
    test_data_href: 'https://plante-receipt-parser.azurewebsites.net/admin/vfs/tmp/FunctionsData/parse_from_url.dat'
  }
}

resource sites_plante_receipt_parser_name_sites_plante_receipt_parser_name_azurewebsites_net 'Microsoft.Web/sites/hostNameBindings@2023-01-01' = {
  parent: sites_plante_receipt_parser_name_resource
  location: 'West Europe'
  name: '${sites_plante_receipt_parser_name}.azurewebsites.net'
  properties: {
    hostNameType: 'Verified'
    siteName: 'plante-receipt-parser'
  }
}



resource smartdetectoralertrules_failure_anomalies_plante_receipt_parser_name_resource 'microsoft.alertsmanagement/smartdetectoralertrules@2021-04-01' = {
  location: 'global'
  name: smartdetectoralertrules_failure_anomalies_plante_receipt_parser_name
  properties: {
    actionGroups: {
      groupIds: [
        actionGroups_Application_Insights_Smart_Detection_name_resource.id
      ]
    }
    description: 'Failure Anomalies notifies you of an unusual rise in the rate of failed HTTP requests or dependency calls.'
    detector: {
      id: 'FailureAnomaliesDetector'
    }
    frequency: 'PT1M'
    scope: [
      components_plante_receipt_parser_name_resource.id
    ]
    severity: 'Sev3'
    state: 'Enabled'
  }
}



resource storageAccounts_plante_name_default_azure_webjobs_hosts 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: storageAccounts_plante_name_default
  name: 'azure-webjobs-hosts'
  properties: {
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
    immutableStorageWithVersioning: {
      enabled: false
    }
    publicAccess: 'None'
  }
  dependsOn: [

    storageAccounts_plante_name_resource
  ]
}

resource storageAccounts_plante_name_default_azure_webjobs_secrets 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: storageAccounts_plante_name_default
  name: 'azure-webjobs-secrets'
  properties: {
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
    immutableStorageWithVersioning: {
      enabled: false
    }
    publicAccess: 'None'
  }
  dependsOn: [

    storageAccounts_plante_name_resource
  ]
}

resource storageAccounts_plante_name_default_scm_releases 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: storageAccounts_plante_name_default
  name: 'scm-releases'
  properties: {
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
    immutableStorageWithVersioning: {
      enabled: false
    }
    publicAccess: 'None'
  }
  dependsOn: [

    storageAccounts_plante_name_resource
  ]
}

resource storageAccounts_plante_name_default_storageAccounts_plante_name_receipt_parserab26 'Microsoft.Storage/storageAccounts/fileServices/shares@2023-01-01' = {
  parent: Microsoft_Storage_storageAccounts_fileServices_storageAccounts_plante_name_default
  name: '${storageAccounts_plante_name}-receipt-parserab26'
  properties: {
    accessTier: 'TransactionOptimized'
    enabledProtocols: 'SMB'
    shareQuota: 5120
  }
  dependsOn: [

    storageAccounts_plante_name_resource
  ]
}
