Set-StrictMode -Version Latest

function Get-PortfolioRoot {
    return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
}

function Get-PortfolioBrowser {
    $candidates = @(
        'C:\Program Files\Google\Chrome\Application\chrome.exe',
        'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) { return $candidate }
    }

    throw 'No se encontró Google Chrome ni Microsoft Edge.'
}

function ConvertTo-FileUrl {
    param([Parameter(Mandatory)][string]$Path)
    $resolved = (Resolve-Path -LiteralPath $Path).Path
    return ([System.Uri]::new($resolved)).AbsoluteUri
}

function Wait-GeneratedFile {
    param(
        [Parameter(Mandatory)][string]$Path,
        [int]$TimeoutSeconds = 20
    )

    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    do {
        if (Test-Path -LiteralPath $Path) {
            $file = Get-Item -LiteralPath $Path
            if ($file.Length -gt 0) { return }
        }
        Start-Sleep -Milliseconds 150
    } while ([DateTime]::UtcNow -lt $deadline)

    throw "No se generó el archivo esperado: $Path"
}
