[CmdletBinding()]
param(
    [switch]$SkipSlides
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common.ps1')

$projectRoot = Get-PortfolioRoot
$browser = Get-PortfolioBrowser
$indexPath = Join-Path $projectRoot 'index.html'
$indexUrl = ConvertTo-FileUrl -Path $indexPath
$distPath = Join-Path $projectRoot 'dist'
$slidesPath = Join-Path $distPath 'slides'
$profilePath = Join-Path $projectRoot '.chrome-profile'
$pdfPath = Join-Path $distPath 'Benjamin_Luduena_Portafolio_Soporte_IT.pdf'

New-Item -ItemType Directory -Path $distPath, $slidesPath, $profilePath -Force | Out-Null

$commonArguments = @(
    '--headless=new',
    '--disable-gpu',
    '--disable-extensions',
    '--disable-background-mode',
    '--no-first-run',
    '--no-default-browser-check',
    '--hide-scrollbars',
    '--allow-file-access-from-files',
    '--run-all-compositor-stages-before-draw',
    '--virtual-time-budget=1500'
)

Write-Host 'Generando PDF del portafolio...' -ForegroundColor Cyan
if (Test-Path -LiteralPath $pdfPath) { Remove-Item -LiteralPath $pdfPath -Force }
$pdfProfile = Join-Path $profilePath ('pdf-' + [guid]::NewGuid().ToString('N'))
& $browser @commonArguments "--user-data-dir=$pdfProfile" '--no-pdf-header-footer' "--print-to-pdf=$pdfPath" $indexUrl
Wait-GeneratedFile -Path $pdfPath

if (-not $SkipSlides) {
    Write-Host 'Generando diez imágenes individuales...' -ForegroundColor Cyan
    for ($slide = 1; $slide -le 10; $slide++) {
        $output = Join-Path $slidesPath ('slide-{0:D2}.png' -f $slide)
        if (Test-Path -LiteralPath $output) { Remove-Item -LiteralPath $output -Force }
        $url = '{0}?slide={1}&export=1' -f $indexUrl, $slide
        $slideProfile = Join-Path $profilePath ('slide-{0:D2}-{1}' -f $slide, [guid]::NewGuid().ToString('N'))
        & $browser @commonArguments "--user-data-dir=$slideProfile" '--window-size=1080,1350' "--screenshot=$output" $url
        Wait-GeneratedFile -Path $output
    }
}

Write-Host "PDF listo: $pdfPath" -ForegroundColor Green
if (-not $SkipSlides) { Write-Host "Imágenes listas: $slidesPath" -ForegroundColor Green }
