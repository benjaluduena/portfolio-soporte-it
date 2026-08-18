<#
.SYNOPSIS
    Reúne información básica de diagnóstico de un equipo Windows.

.DESCRIPTION
    Script de solo lectura pensado como apoyo para una mesa de ayuda. Consulta
    sistema operativo, hardware, almacenamiento, red, DNS y conectividad. No
    modifica configuraciones ni requiere permisos de administrador.

.PARAMETER OutputPath
    Ruta del archivo JSON. Por defecto crea un informe fechado en la carpeta
    "reports", junto al script.

.PARAMETER ConnectivityTarget
    Host usado para comprobar resolución DNS y conectividad. El valor por
    defecto es example.com.

.EXAMPLE
    .\Get-SystemDiagnostic.ps1

.EXAMPLE
    .\Get-SystemDiagnostic.ps1 -OutputPath "$env:TEMP\diagnostico.json"
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$OutputPath,

    [Parameter()]
    [ValidateNotNullOrEmpty()]
    [string]$ConnectivityTarget = 'example.com'
)

$ErrorActionPreference = 'Stop'

if (-not $OutputPath) {
    $reportDirectory = Join-Path -Path $PSScriptRoot -ChildPath 'reports'
    $OutputPath = Join-Path -Path $reportDirectory -ChildPath (
        'SystemDiagnostic-{0}.json' -f (Get-Date -Format 'yyyyMMdd-HHmmss')
    )
}

$resolvedOutputPath = [System.IO.Path]::GetFullPath($OutputPath)
$outputDirectory = Split-Path -Path $resolvedOutputPath -Parent
if (-not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
}

function Invoke-SafeQuery {
    param(
        [Parameter(Mandatory)]
        [scriptblock]$Query
    )

    try {
        & $Query
    }
    catch {
        [pscustomobject]@{ Error = $_.Exception.Message }
    }
}

$operatingSystem = Invoke-SafeQuery {
    Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object `
        Caption, Version, BuildNumber, OSArchitecture, LastBootUpTime
}

$computerSystem = Invoke-SafeQuery {
    Get-CimInstance -ClassName Win32_ComputerSystem | Select-Object `
        Manufacturer, Model, TotalPhysicalMemory, Domain, PartOfDomain
}

$processor = Invoke-SafeQuery {
    Get-CimInstance -ClassName Win32_Processor | Select-Object `
        Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed
}

$disks = Invoke-SafeQuery {
    Get-CimInstance -ClassName Win32_LogicalDisk -Filter 'DriveType = 3' |
        Select-Object DeviceID, VolumeName,
        @{ Name = 'SizeGB'; Expression = { [math]::Round($_.Size / 1GB, 2) } },
        @{ Name = 'FreeGB'; Expression = { [math]::Round($_.FreeSpace / 1GB, 2) } },
        @{ Name = 'FreePercent'; Expression = {
            if ($_.Size) { [math]::Round(($_.FreeSpace / $_.Size) * 100, 1) } else { 0 }
        } }
}

$networkAdapters = Invoke-SafeQuery {
    Get-NetIPConfiguration | ForEach-Object {
        [pscustomobject]@{
            InterfaceAlias = $_.InterfaceAlias
            InterfaceDescription = $_.InterfaceDescription
            IPv4Address = @($_.IPv4Address.IPAddress)
            IPv6Address = @($_.IPv6Address.IPAddress)
            DefaultGateway = @($_.IPv4DefaultGateway.NextHop)
            DnsServers = @($_.DNSServer.ServerAddresses)
        }
    }
}

$dnsResolution = Invoke-SafeQuery {
    Resolve-DnsName -Name $ConnectivityTarget -ErrorAction Stop |
        Select-Object Name, Type, IPAddress
}

$connectivity = Invoke-SafeQuery {
    Test-NetConnection -ComputerName $ConnectivityTarget -InformationLevel Detailed |
        Select-Object ComputerName, RemoteAddress, NameResolutionSucceeded,
        PingSucceeded
}

$report = [ordered]@{
    SchemaVersion = '1.0'
    GeneratedAt = (Get-Date).ToString('o')
    ComputerName = $env:COMPUTERNAME
    CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    OperatingSystem = $operatingSystem
    ComputerSystem = $computerSystem
    Processor = $processor
    Disks = @($disks)
    NetworkAdapters = @($networkAdapters)
    ConnectivityTarget = $ConnectivityTarget
    DnsResolution = @($dnsResolution)
    Connectivity = $connectivity
}

$report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $resolvedOutputPath -Encoding utf8

Write-Host "Informe generado: $resolvedOutputPath" -ForegroundColor Green
Write-Warning 'Revisá el archivo antes de compartirlo: puede contener nombres de usuario, equipo, dominio y direcciones IP.'
