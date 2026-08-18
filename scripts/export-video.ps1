[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common.ps1')

$projectRoot = Get-PortfolioRoot
$browser = Get-PortfolioBrowser
$ffmpegCommand = Get-Command ffmpeg -ErrorAction Stop
$videoSource = Join-Path $projectRoot 'video\demo.html'
$videoUrl = ConvertTo-FileUrl -Path $videoSource
$distPath = Join-Path $projectRoot 'dist'
$framesPath = Join-Path $distPath 'video-frames'
$profilePath = Join-Path $projectRoot '.chrome-profile'
$outputPath = Join-Path $distPath 'Benjamin_Luduena_Demo_SoporteLab.mp4'

New-Item -ItemType Directory -Path $distPath, $framesPath, $profilePath -Force | Out-Null

$browserArguments = @(
    '--headless=new',
    '--disable-gpu',
    '--disable-extensions',
    '--disable-background-mode',
    '--no-first-run',
    '--no-default-browser-check',
    '--hide-scrollbars',
    '--allow-file-access-from-files',
    '--run-all-compositor-stages-before-draw',
    '--virtual-time-budget=1200',
    '--window-size=1920,1080'
)

Write-Host 'Generando escenas del video...' -ForegroundColor Cyan
for ($scene = 1; $scene -le 7; $scene++) {
    $output = Join-Path $framesPath ('scene-{0:D2}.png' -f $scene)
    if (Test-Path -LiteralPath $output) { Remove-Item -LiteralPath $output -Force }
    $url = '{0}?scene={1}' -f $videoUrl, $scene
    $sceneProfile = Join-Path $profilePath ('scene-{0:D2}-{1}' -f $scene, [guid]::NewGuid().ToString('N'))
    & $browser @browserArguments "--user-data-dir=$sceneProfile" "--screenshot=$output" $url
    Wait-GeneratedFile -Path $output
}

$concatPath = Join-Path $framesPath 'concat.txt'
$concatLines = [System.Collections.Generic.List[string]]::new()
for ($scene = 1; $scene -le 7; $scene++) {
    $concatLines.Add("file 'scene-{0:D2}.png'" -f $scene)
    $concatLines.Add('duration 8.5')
}
$concatLines.Add("file 'scene-07.png'")
[System.IO.File]::WriteAllLines(
    $concatPath,
    [string[]]$concatLines,
    [System.Text.UTF8Encoding]::new($false)
)

Write-Host 'Codificando video MP4 de aproximadamente 60 segundos...' -ForegroundColor Cyan
if (Test-Path -LiteralPath $outputPath) { Remove-Item -LiteralPath $outputPath -Force }
Push-Location $framesPath
try {
    & $ffmpegCommand.Source -y -loglevel warning -f concat -safe 0 -i 'concat.txt' -vf 'fps=30,format=yuv420p' -c:v libx264 -preset medium -crf 18 -movflags '+faststart' $outputPath
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $outputPath)) {
        throw 'ffmpeg no pudo generar el video.'
    }
}
finally {
    Pop-Location
}

Write-Host "Video listo: $outputPath" -ForegroundColor Green
