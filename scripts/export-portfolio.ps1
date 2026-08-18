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
$contactSheetPath = Join-Path $distPath 'contact-sheet.png'

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

    $ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
    if ($ffmpeg) {
        Write-Host 'Generando vista previa de las diez páginas...' -ForegroundColor Cyan
        $inputArguments = @()
        for ($slide = 1; $slide -le 10; $slide++) {
            $inputArguments += '-i'
            $inputArguments += (Join-Path $slidesPath ('slide-{0:D2}.png' -f $slide))
        }

        $scaleFilters = 0..9 | ForEach-Object {
            '[{0}:v]scale=264:330,pad=276:342:6:6:color=#dce1dd[s{0}]' -f $_
        }
        $filter = ($scaleFilters -join ';') +
            ';[s0][s1][s2][s3][s4]hstack=inputs=5[top]' +
            ';[s5][s6][s7][s8][s9]hstack=inputs=5[bottom]' +
            ';[top][bottom]vstack=inputs=2[out]'

        & $ffmpeg.Source -hide_banner -loglevel error -y @inputArguments -filter_complex $filter -map '[out]' -frames:v 1 $contactSheetPath
        if ($LASTEXITCODE -ne 0) { throw 'No se pudo generar la vista previa del portafolio.' }
        Wait-GeneratedFile -Path $contactSheetPath
    }
    else {
        Write-Warning 'ffmpeg no está disponible; se omitió la vista previa de las diez páginas.'
    }
}

Write-Host "PDF listo: $pdfPath" -ForegroundColor Green
if (-not $SkipSlides) { Write-Host "Imágenes listas: $slidesPath" -ForegroundColor Green }
if (-not $SkipSlides -and (Test-Path -LiteralPath $contactSheetPath)) { Write-Host "Vista previa lista: $contactSheetPath" -ForegroundColor Green }
