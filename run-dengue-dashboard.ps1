$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $projectRoot 'chonburi-dengue-watch\backend'
$frontendDir = Join-Path $projectRoot 'chonburi-dengue-watch\frontend'
$portableNodeDir = Join-Path $projectRoot '.tools\node'
$portablePythonDir = Join-Path $projectRoot '.tools\python'
$logDir = Join-Path $projectRoot '.logs'
$runStamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backendLog = Join-Path $logDir "backend-$runStamp.log"
$frontendLog = Join-Path $logDir "frontend-$runStamp.log"
$backendPort = 8000
$frontendPort = 5173
$adminToken = [guid]::NewGuid().ToString('N')

function Show-Banner {
    Write-Host "" 
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "  Chonburi Dengue Dashboard Launcher" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Ensure-PortableNode {
    if (Get-Command node -ErrorAction SilentlyContinue) {
        return
    }

    $toolsDir = Join-Path $projectRoot '.tools'
    New-Item -ItemType Directory -Force -Path $toolsDir | Out-Null

    $releaseUrl = 'https://nodejs.org/dist/index.json'
    $releaseList = Invoke-RestMethod -Uri $releaseUrl -UseBasicParsing
    $release = $null
    foreach ($item in $releaseList) {
        if ($item.lts -and $item.version -match '^v\d+\.\d+\.\d+$') {
            $candidateVersion = [version]($item.version.TrimStart('v'))
            if (-not $release -or $candidateVersion -gt $release.Version) {
                $release = [pscustomobject]@{
                    Version = $candidateVersion
                    Value = $item.version
                }
            }
        }
    }

    if (-not $release) {
        Write-Host 'Unable to fetch the latest Node.js LTS release.' -ForegroundColor Red
        Read-Host 'Press Enter to exit'
        exit 1
    }

    $version = $release.Value
    $archiveName = "node-$version-win-x64.zip"
    $archiveUrl = "https://nodejs.org/dist/$version/$archiveName"
    $archivePath = Join-Path $toolsDir $archiveName
    $nodeExtractDir = Join-Path $toolsDir "node-$version-win-x64"

    if (-not (Test-Path $portableNodeDir)) {
        Write-Host "[node] not found. Downloading portable Node.js LTS..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $archiveUrl -UseBasicParsing -OutFile $archivePath
        Expand-Archive -Path $archivePath -DestinationPath $toolsDir -Force
        if (Test-Path $nodeExtractDir) {
            Move-Item -Path $nodeExtractDir -Destination $portableNodeDir -Force
        }
    }

    if (-not (Test-Path (Join-Path $portableNodeDir 'node.exe'))) {
        Write-Host 'Portable Node.js was not extracted correctly.' -ForegroundColor Red
        Read-Host 'Press Enter to exit'
        exit 1
    }

    $env:Path = "$portableNodeDir;$env:Path"
}

function Write-StatusBadge {
    param(
        [string]$BackendStatus,
        [string]$FrontendStatus,
        [bool]$Final = $false
    )

    $backendText = if ($BackendStatus -eq 'ready') { '[ READY ] Backend' } else { '[ STARTING ] Backend' }
    $frontendText = if ($FrontendStatus -eq 'ready') { '[ READY ] Frontend' } else { '[ STARTING ] Frontend' }

    if ($Final) {
        Write-Host "" 
        Write-Host "LIVE STATUS`n$backendText | $frontendText" -ForegroundColor Green
        Write-Host "" 
    }
    else {
        Write-Host ("LIVE STATUS :: {0} | {1}" -f $backendText, $frontendText) -ForegroundColor Cyan
    }
}

function Wait-ForUrl {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 120
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return $true
            }
        }
        catch {
            Start-Sleep -Seconds 1
        }
    }
    return $false
}

function Test-PortInUse {
    param([int]$Port)
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $client.Connect('127.0.0.1', $Port)
        return $true
    }
    catch {
        return $false
    }
    finally {
        $client.Dispose()
    }
}

function Stop-TrackedProcesses {
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessId -ne $PID -and
        $_.CommandLine -and
        ($_.CommandLine.IndexOf($projectRoot, [System.StringComparison]::OrdinalIgnoreCase) -ge 0 -or $_.CommandLine -match 'chonburi-dengue-watch|run-dengue-dashboard') -and
        $_.Name -in @('cmd.exe', 'python.exe', 'node.exe', 'npm.exe')
    } | ForEach-Object {
        try { $_.Terminate() | Out-Null } catch {}
    }
}

function Stop-LauncherServices {
    param(
        $BackendJob,
        $FrontendJob
    )

    foreach ($job in @($BackendJob, $FrontendJob)) {
        if ($null -ne $job) {
            try { Stop-Job -Job $job -ErrorAction Stop } catch {}
            try { Remove-Job -Job $job -Force -ErrorAction SilentlyContinue } catch {}
        }
    }
    Stop-TrackedProcesses
}

Show-Banner

$portablePython = Join-Path $portablePythonDir 'python.exe'
$pythonCmd = if (Test-Path $portablePython) { Get-Item $portablePython } else { Get-Command python -ErrorAction SilentlyContinue }
if (-not $pythonCmd) {
    Write-Host 'Python was not found in PATH.' -ForegroundColor Red
    Write-Host 'Please install Python 3.10+ and rerun this script.' -ForegroundColor Red
    Read-Host 'Press Enter to exit'
    exit 1
}
$env:PYTHONUTF8 = '1'
$pythonExe = $pythonCmd.FullName

New-Item -Path $logDir -ItemType Directory -Force | Out-Null
Stop-TrackedProcesses
foreach ($logFile in @($backendLog, $frontendLog)) {
    for ($attempt = 0; $attempt -lt 5 -and (Test-Path $logFile); $attempt++) {
        try { Remove-Item $logFile -Force -ErrorAction Stop } catch { Start-Sleep -Milliseconds 250 }
    }
}

Ensure-PortableNode

Write-Host '[1/3] Checking environment...' -ForegroundColor Green
Write-Host "Python: $pythonExe" -ForegroundColor Gray
Write-Host "Node:   $(Get-Command node | Select-Object -ExpandProperty Source)" -ForegroundColor Gray

Write-Host '[2/3] Installing backend dependencies...' -ForegroundColor Green
Push-Location $backendDir
& $pythonExe -m pip install -r requirements.txt | Out-Null
Pop-Location

Write-Host '[3/3] Launching backend and frontend services...' -ForegroundColor Green

while (Test-PortInUse -Port $backendPort) {
    $backendPort++
}
if ($backendPort -ne 8000) {
    Write-Host "Backend port 8000 is already in use. Using port $backendPort for this session." -ForegroundColor Yellow
}
while (Test-PortInUse -Port $frontendPort) {
    $frontendPort++
}
if ($frontendPort -ne 5173) {
    Write-Host "Frontend port 5173 is already in use. Using port $frontendPort for this session." -ForegroundColor Yellow
}
$backendUrl = "http://localhost:$backendPort"
$backendCommand = "/c cd /d `"$backendDir`" && set `"PYTHONUTF8=1`" && set `"DENGUE_ADMIN_TOKEN=$adminToken`" && `"$pythonExe`" -m uvicorn app.main:app --host 0.0.0.0 --port $backendPort >> `"$backendLog`" 2>&1"
$frontendCommand = "/c cd /d `"$frontendDir`" && set `"VITE_API_URL=$backendUrl`" && call `"$(Join-Path $portableNodeDir 'npm.cmd')`" install >> `"$frontendLog`" 2>&1 && set `"VITE_API_URL=$backendUrl`" && call `"$(Join-Path $portableNodeDir 'npm.cmd')`" run dev -- --host 0.0.0.0 --port $frontendPort >> `"$frontendLog`" 2>&1"

Start-Process -FilePath 'cmd.exe' -ArgumentList $backendCommand -WindowStyle Hidden | Out-Null
Start-Process -FilePath 'cmd.exe' -ArgumentList $frontendCommand -WindowStyle Hidden | Out-Null

Write-Host "" 
Write-Host 'Logs:' -ForegroundColor Yellow
Write-Host "  Backend: $backendLog" -ForegroundColor Gray
Write-Host "  Frontend: $frontendLog" -ForegroundColor Gray
Write-Host "  Reset admin token: $adminToken" -ForegroundColor Yellow
Write-Host "" 

$backendReady = $false
$frontendReady = $false

while (-not ($backendReady -and $frontendReady)) {
    if (-not $backendReady) {
        $backendReady = Wait-ForUrl -Url "$backendUrl/docs" -TimeoutSeconds 20
        if ($backendReady) {
            Write-StatusBadge -BackendStatus 'ready' -FrontendStatus 'starting'
        }
    }

    if (-not $frontendReady) {
        $frontendReady = Wait-ForUrl -Url "http://localhost:$frontendPort" -TimeoutSeconds 20
        if ($frontendReady) {
            Write-StatusBadge -BackendStatus 'ready' -FrontendStatus 'ready'
        }
    }

    if (-not ($backendReady -and $frontendReady)) {
        Start-Sleep -Seconds 2
    }
}

Write-Host "" 
Write-Host "Backend API: $backendUrl/docs" -ForegroundColor Cyan
Write-Host "Dashboard:   http://localhost:$frontendPort" -ForegroundColor Cyan
Write-Host 'Landing:     http://localhost:8080/portfolio-landing.html' -ForegroundColor Cyan
Write-Host "" 
Write-StatusBadge -BackendStatus 'ready' -FrontendStatus 'ready' -Final $true
Write-Host 'Launcher complete. Backend and frontend remain running.' -ForegroundColor Green
Write-Host 'Close services manually with the project stop command when finished.' -ForegroundColor Yellow
exit 0
