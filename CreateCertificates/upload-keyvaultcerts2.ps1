#*********************************************************
#
# Copyright (c) Microsoft. All rights reserved.
# This code is licensed under the MIT License (MIT).
# THIS CODE IS PROVIDED *AS IS* WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING ANY
# IMPLIED WARRANTIES OF FITNESS FOR A PARTICULAR
# PURPOSE, MERCHANTABILITY, OR NON-INFRINGEMENT.
#
#*********************************************************

param
(
    [Parameter(Mandatory = $True)]
    [string] $SubscriptionId,

    [Parameter(Mandatory = $True)]
    [string] $KeyVaultName
    
)

###########################################################################
#
# Connect-AzureSubscription - gets current Azure context or triggers a 
# user log in to Azure. Selects the Azure subscription for creation of 
# the virtual machine   
# 

Set-AzureRmKeyVaultAccessPolicy -VaultName $KeyVaultName -UserPrincipalName 'andrei.ciobanu_aimsoftware.com#EXT#@andreiciobanuaimsoftware.onmicrosoft.com' -PermissionsToCertificates create, import, update, list -PermissionsToSecrets get, list, set, delete

$results=@()
$pth=Get-Location
foreach ($item in Get-ChildItem -Path $pth -Recurse -File) {
    $certificateName = ($item.Name).Replace(".", "-")
    $filePath = $item.FullName
    if ($item.Name -Like "*.pfx") {
        Write-Host "Uploading $($item.Name)..."
        $password = ConvertTo-SecureString "1234" -AsPlainText -Force
        $certificate = Import-AzureKeyVaultCertificate -VaultName $KeyVaultName -Name $certificateName -FilePath $filePath -Password $password
        $results += (@{"Certificate"=$item.Name;"KeyVaultName"=$certificate.Name;"KeyVaultId"=$certificate.Id})
    }

    if ($item.Name -Like "*.pem") {
        $pemString = [IO.File]::ReadAllText($item.FullName)
        $pemAsSecret = ConvertTo-SecureString $pemString -AsPlainText -Force
        Write-Host "Uploading $($item.Name)..."
        $secret = Set-AzureKeyVaultSecret -VaultName $KeyVaultName  -Name $certificateName -SecretValue $pemAsSecret
        $results += (@{"Certificate"=$item.Name;"KeyVaultName"=$secret.Name;"KeyVaultId"=$secret.Id})
    }
}

Write-Host "Results:"
$results.foreach({[PSCustomObject]$_}) | Format-Table "Certificate", "KeyVaultName", "KeyVaultId" -AutoSize
