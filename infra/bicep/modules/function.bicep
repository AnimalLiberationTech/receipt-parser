param organizationName string = 'plante'
param applicationName string = 'receipt-parser'
param environment string = 'dev'
param location string = 'West Europe'
param environmentVariables array
param resourceTags object = {}

resource storageAccount 'Microsoft.Storage/storageAccounts@2019-06-01' = {
  name: '${organizationName}receiptparser'
  location: location
  kind: 'StorageV2'
  tags: resourceTags
  properties: {
    allowBlobPublicAccess: false
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
  }
}

resource defaultBlobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
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
}

resource defaultFileService 'Microsoft.Storage/storageAccounts/fileServices@2023-01-01' = {
  parent: storageAccount
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
}

resource defaultQueueService 'Microsoft.Storage/storageAccounts/queueServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    cors: {
      corsRules: []
    }
  }
}

resource defaultTableService 'Microsoft.Storage/storageAccounts/tableServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    cors: {
      corsRules: []
    }
  }
}

resource storageAccountWebjobsHost 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: defaultBlobService
  name: 'webjobs-hosts'
  properties: {
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
    immutableStorageWithVersioning: {
      enabled: false
    }
    publicAccess: 'None'
  }
  dependsOn: []
}

resource storageAccountWebjobsSecrets 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: defaultBlobService
  name: 'webjobs-secrets'
  properties: {
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
    immutableStorageWithVersioning: {
      enabled: false
    }
    publicAccess: 'None'
  }
  dependsOn: []
}

resource storageAccountScmReleases 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: defaultBlobService
  name: 'scm-releases'
  properties: {
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
    immutableStorageWithVersioning: {
      enabled: false
    }
    publicAccess: 'None'
  }
  dependsOn: []
}

resource storageAccountFileShare 'Microsoft.Storage/storageAccounts/fileServices/shares@2023-01-01' = {
  parent: defaultFileService
  name: 'files-${organizationName}-${applicationName}-${environment}'
  properties: {
    accessTier: 'TransactionOptimized'
    enabledProtocols: 'SMB'
    shareQuota: 5120
  }
  dependsOn: []
}

resource hostingPlan 'Microsoft.Web/serverfarms@2020-10-01' = {
  name: 'hosting-plan-${organizationName}'
  location: location
  tags: resourceTags
  kind: 'functionapp'
  properties: {
    hyperV: false
    isSpot: false
    isXenon: false
    maximumElasticWorkerCount: 1
    perSiteScaling: false
    reserved: true
    targetWorkerCount: 0
    targetWorkerSizeId: 0
  }
  sku: {
    capacity: 0
    family: 'Y'
    name: 'Y1'
    size: 'Y1'
    tier: 'Dynamic'
  }
}

resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  kind: 'functionapp,linux'
  name: 'app-${applicationName}-${environment}'
  location: location
  properties: {
    serverFarmId: hostingPlan.id
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
        name: '${organizationName}-${applicationName}-${environment}.azurewebsites.net'
        sslState: 'Disabled'
      }
      {
        hostType: 'Repository'
        name: '${organizationName}-${applicationName}-${environment}.scm.azurewebsites.net'
        sslState: 'Disabled'
      }
    ]
    hostNamesDisabled: false
    httpsOnly: true
    hyperV: false
    isXenon: false
    redundancyMode: 'None'
    reserved: true
    scmSiteAlsoStopped: false
    keyVaultReferenceIdentity: 'SystemAssigned'
    publicNetworkAccess: 'Enabled'
    siteConfig: {
      acrUseManagedIdentityCreds: false
      alwaysOn: false
      http20Enabled: false
      linuxFxVersion: 'PYTHON|3.11'
      numberOfWorkers: 1
      appSettings: union(environmentVariables, [
        // {
        //   name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
        //   value: appInsights.properties.InstrumentationKey
        // }
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${az.environment().suffixes.storage};AccountKey=${listKeys(storageAccount.id, storageAccount.apiVersion).keys[0].value}'
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
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${az.environment().suffixes.storage};AccountKey=${listKeys(storageAccount.id, storageAccount.apiVersion).keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: storageAccountFileShare.name
        }
        {
          name: 'FUNCTION_APP_EDIT_MODE'
          value: 'readwrite'
        }
      ])
    }
    storageAccountRequired: false
    vnetContentShareEnabled: false
    vnetImagePullEnabled: false
    vnetRouteAllEnabled: false
  }
}

resource functionAppFtp 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2023-01-01' = {
  parent: functionApp
  name: 'ftp'
  properties: {
    allow: true
  }
}

resource functionAppScm 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2023-01-01' = {
  parent: functionApp
  name: 'scm'
  properties: {
    allow: true
  }
}

resource functionAppWeb 'Microsoft.Web/sites/config@2023-01-01' = {
  parent: functionApp
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
    publishingUsername: '$${organizationName}-${applicationName}'
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
}

resource homeFunction 'Microsoft.Web/sites/functions@2023-01-01' = {
  parent: functionApp
  name: 'home'
  properties: {
    function_app_id: functionApp.id
    script_href: 'https://app-${applicationName}-${environment}.azurewebsites.net/admin/vfs/home/site/wwwroot/function_app.py'
    href: 'https://app-${applicationName}-${environment}.azurewebsites.net/admin/functions/home'
    config: {
      name: 'home'
      entryPoint: 'home'
      scriptFile: 'function_app.py'
      language: 'python'
      functionDirectory: '/home/site/wwwroot'
      bindings: [
        {
          direction: 'IN'
          type: 'httpTrigger'
          name: 'req'
          methods: ['GET']
          authLevel: 'ANONYMOUS'
          route: 'home'
        }
        {
          direction: 'OUT'
          type: 'http'
          name: '$return'
        }
      ]
    }
    files: null
    test_data: ''
    invoke_url_template: 'https://app-${applicationName}-${environment}.azurewebsites.net/api/home'
    language: 'python'
    isDisabled: false
  }
}

output application_url string = functionApp.properties.hostNames[0]
