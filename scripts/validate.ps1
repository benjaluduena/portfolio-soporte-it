[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common.ps1')

$projectRoot = Get-PortfolioRoot
$required = @(
    'index.html',
    'styles.css',
    'app.js',
    'assets\screenshots\dashboard.png',
    'assets\screenshots\tickets.png',
    'assets\screenshots\ticket-detail.png',
    'assets\screenshots\knowledge.png',
    'publicacion\publicacion-linkedin.md',
    'soportelab\manage.py',
    'soportelab\tools\Get-SystemDiagnostic.ps1'
)

foreach ($relativePath in $required) {
    $fullPath = Join-Path $projectRoot $relativePath
    if (-not (Test-Path -LiteralPath $fullPath)) { throw "Falta un archivo requerido: $relativePath" }
}

$html = Get-Content -Raw -Encoding utf8 -LiteralPath (Join-Path $projectRoot 'index.html')
$slideCount = [regex]::Matches($html, 'data-slide="\d+"').Count
if ($slideCount -ne 10) { throw "Se esperaban 10 páginas y se encontraron $slideCount." }

$distPath = Join-Path $projectRoot 'dist'
$pdfPath = Join-Path $distPath 'Benjamin_Luduena_Portafolio_Soporte_IT.pdf'
$videoPath = Join-Path $distPath 'Benjamin_Luduena_Demo_SoporteLab.mp4'

if (Test-Path -LiteralPath $pdfPath) {
    $pdfSize = (Get-Item -LiteralPath $pdfPath).Length
    if ($pdfSize -lt 100000) { throw 'El PDF generado parece incompleto.' }
    Write-Host ('PDF: {0:N1} MB' -f ($pdfSize / 1MB)) -ForegroundColor Green
}

if (Test-Path -LiteralPath $videoPath) {
    $ffprobe = Get-Command ffprobe -ErrorAction SilentlyContinue
    if ($ffprobe) {
        $duration = & $ffprobe.Source -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $videoPath
        Write-Host ('Video: {0:N1} segundos' -f [double]$duration) -ForegroundColor Green
    }
}

$localPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
$pythonPath = if (Test-Path -LiteralPath $localPython) {
    $localPython
}
else {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) { $pythonCommand.Source } else { $null }
}
if ($pythonPath) {
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'SilentlyContinue'
    & $pythonPath -c 'import django' 2>$null
    $djangoAvailable = $LASTEXITCODE -eq 0
    $ErrorActionPreference = $previousPreference
    if ($djangoAvailable) {
        Push-Location (Join-Path $projectRoot 'soportelab')
        try {
            & $pythonPath manage.py check
            if ($LASTEXITCODE -ne 0) { throw 'manage.py check informó errores.' }
            & $pythonPath manage.py test
            if ($LASTEXITCODE -ne 0) { throw 'Las pruebas de SoporteLab fallaron.' }
        }
        finally { Pop-Location }
    }
    else {
        Write-Warning 'Django no está instalado en el Python activo; se omitieron las pruebas de la aplicación.'
    }
}

Write-Host 'Validación estructural completada.' -ForegroundColor Green
