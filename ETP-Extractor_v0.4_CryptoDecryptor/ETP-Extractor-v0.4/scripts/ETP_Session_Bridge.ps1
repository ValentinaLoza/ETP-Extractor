param(
    [int]$DebugPort = 9222,
    [string]$ApiPath = "/api/library",
    [string]$OutputDirectory = "",
    [switch]$DoNotLaunchETP
)

$ErrorActionPreference = "Stop"

function Write-Step([string]$Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Find-EtpExecutable {
    $candidates = @(
        (Join-Path $env:APPDATA "PWC\ETP-Premium\client\ETP Offline Premium.exe"),
        (Join-Path $env:APPDATA "PWC\ETP-Premium\client\ETP Offline Premium\ETP Offline Premium.exe"),
        (Join-Path $env:LOCALAPPDATA "PWC\ETP-Premium\client\ETP Offline Premium.exe")
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    $root = Join-Path $env:APPDATA "PWC\ETP-Premium"
    if (Test-Path $root) {
        $found = Get-ChildItem -Path $root -Filter "ETP Offline Premium.exe" -Recurse -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($found) {
            return $found.FullName
        }
    }

    return $null
}

function Wait-ForDevTools([int]$Port, [int]$TimeoutSeconds = 30) {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $targets = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/json" -TimeoutSec 2
            if ($targets) {
                return $targets
            }
        }
        catch {
            Start-Sleep -Milliseconds 700
        }
    }
    throw "No se pudo conectar a Chrome DevTools en el puerto $Port."
}

function Receive-WebSocketMessage {
    param(
        [System.Net.WebSockets.ClientWebSocket]$Socket,
        [int]$TimeoutSeconds = 30
    )

    $buffer = New-Object byte[] 65536
    $memory = New-Object System.IO.MemoryStream
    $cts = New-Object System.Threading.CancellationTokenSource
    $cts.CancelAfter([TimeSpan]::FromSeconds($TimeoutSeconds))

    try {
        do {
            $segment = New-Object System.ArraySegment[byte] -ArgumentList @(,$buffer)
            $result = $Socket.ReceiveAsync($segment, $cts.Token).GetAwaiter().GetResult()
            if ($result.MessageType -eq [System.Net.WebSockets.WebSocketMessageType]::Close) {
                throw "La conexión DevTools se cerró antes de recibir la respuesta."
            }
            $memory.Write($buffer, 0, $result.Count)
        } while (-not $result.EndOfMessage)

        return [System.Text.Encoding]::UTF8.GetString($memory.ToArray())
    }
    finally {
        $memory.Dispose()
        $cts.Dispose()
    }
}

function Invoke-CdpEvaluate {
    param(
        [string]$WebSocketUrl,
        [string]$Expression
    )

    $socket = New-Object System.Net.WebSockets.ClientWebSocket
    $uri = [Uri]$WebSocketUrl
    $socket.ConnectAsync($uri, [Threading.CancellationToken]::None).GetAwaiter().GetResult()

    try {
        $requestId = 1
        $payload = @{
            id = $requestId
            method = "Runtime.evaluate"
            params = @{
                expression = $Expression
                awaitPromise = $true
                returnByValue = $true
                userGesture = $true
            }
        } | ConvertTo-Json -Depth 10 -Compress

        $bytes = [Text.Encoding]::UTF8.GetBytes($payload)
        $segment = New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes)
        $socket.SendAsync(
            $segment,
            [System.Net.WebSockets.WebSocketMessageType]::Text,
            $true,
            [Threading.CancellationToken]::None
        ).GetAwaiter().GetResult()

        while ($true) {
            $raw = Receive-WebSocketMessage -Socket $socket
            $message = $raw | ConvertFrom-Json
            if ($message.id -eq $requestId) {
                return $message
            }
        }
    }
    finally {
        if ($socket.State -eq [System.Net.WebSockets.WebSocketState]::Open) {
            $socket.CloseAsync(
                [System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure,
                "done",
                [Threading.CancellationToken]::None
            ).GetAwaiter().GetResult()
        }
        $socket.Dispose()
    }
}

if (-not $OutputDirectory) {
    $OutputDirectory = Join-Path $PSScriptRoot ("ETP_Session_Report_" + (Get-Date -Format "yyyyMMdd_HHmmss"))
}
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null

Write-Host "ETP Session Bridge v0.3" -ForegroundColor Green
Write-Host "No muestra ni guarda el token de sesión."
Write-Host "Salida: $OutputDirectory"

if (-not $DoNotLaunchETP) {
    Write-Step "Localizando ETP Offline Premium"
    $etpExe = Find-EtpExecutable
    if (-not $etpExe) {
        throw "No se encontró 'ETP Offline Premium.exe'."
    }
    Write-Host "Encontrado: $etpExe"

    $running = Get-Process -Name "ETP Offline Premium" -ErrorAction SilentlyContinue
    if ($running) {
        Write-Host ""
        Write-Host "ETP está abierto y debe reiniciarse con el puerto de depuración." -ForegroundColor Yellow
        Write-Host "Guardá lo que estés viendo y cerrá ETP."
        Read-Host "Presioná Enter cuando ETP esté completamente cerrado"

        $stillRunning = Get-Process -Name "ETP Offline Premium" -ErrorAction SilentlyContinue
        if ($stillRunning) {
            throw "ETP todavía está abierto. Cerralo desde la aplicación o el Administrador de tareas."
        }
    }

    Write-Step "Abriendo ETP con depuración local"
    Start-Process -FilePath $etpExe -ArgumentList "--remote-debugging-port=$DebugPort"
}

Write-Step "Esperando la ventana de ETP"
$targets = Wait-ForDevTools -Port $DebugPort -TimeoutSeconds 45

$pageTargets = @($targets | Where-Object {
    $_.type -eq "page" -and
    $_.webSocketDebuggerUrl -and
    ($_.url -match "localhost|127\.0\.0\.1")
})

if (-not $pageTargets) {
    $pageTargets = @($targets | Where-Object {
        $_.type -eq "page" -and $_.webSocketDebuggerUrl
    })
}

if (-not $pageTargets) {
    $targets | ConvertTo-Json -Depth 10 |
        Out-File (Join-Path $OutputDirectory "devtools_targets.json") -Encoding utf8
    throw "No se encontró una ventana de ETP compatible. Se guardó devtools_targets.json."
}

$target = $pageTargets | Select-Object -First 1
Write-Host "Ventana seleccionada:"
Write-Host "  Título: $($target.title)"
Write-Host "  URL:    $($target.url)"

Write-Step "Consultando la API desde la sesión oficial de ETP"

# Se usa window.ipc.getToken(), pero el token nunca se devuelve al script.
# La consulta y el agregado del token se ejecutan dentro de la ventana oficial.
$escapedPath = $ApiPath.Replace("\", "\\").Replace("'", "\'")
$expression = @"
(async () => {
  try {
    if (!window.ipc || typeof window.ipc.getToken !== 'function') {
      return {
        ok: false,
        stage: 'ipc',
        error: 'window.ipc.getToken no está disponible en esta ventana',
        pageUrl: location.href
      };
    }

    const token = await window.ipc.getToken();
    if (!token) {
      return {
        ok: false,
        stage: 'token',
        error: 'La sesión de ETP no contiene un token',
        pageUrl: location.href
      };
    }

    const separator = '$escapedPath'.includes('?') ? '&' : '?';
    const requestUrl = '$escapedPath' + separator + 'token=' + encodeURIComponent(token);

    const response = await fetch(requestUrl, {
      method: 'GET',
      credentials: 'same-origin',
      cache: 'no-store',
      headers: {
        'Accept': 'application/json, text/plain, */*'
      }
    });

    const text = await response.text();
    return {
      ok: response.ok,
      status: response.status,
      statusText: response.statusText,
      contentType: response.headers.get('content-type'),
      finalUrl: response.url,
      redirected: response.redirected,
      body: text
    };
  } catch (error) {
    return {
      ok: false,
      stage: 'request',
      error: String(error),
      stack: error && error.stack ? String(error.stack) : null
    };
  }
})()
"@

$resultMessage = Invoke-CdpEvaluate `
    -WebSocketUrl $target.webSocketDebuggerUrl `
    -Expression $expression

$resultMessage |
    ConvertTo-Json -Depth 30 |
    Out-File (Join-Path $OutputDirectory "cdp_raw_response.json") -Encoding utf8

if ($resultMessage.result.exceptionDetails) {
    throw "La evaluación en ETP produjo una excepción. Revisá cdp_raw_response.json."
}

$value = $resultMessage.result.result.value
if (-not $value) {
    throw "ETP no devolvió un resultado por valor. Revisá cdp_raw_response.json."
}

$metadata = [ordered]@{
    generatedAt = (Get-Date).ToString("o")
    apiPath = $ApiPath
    targetTitle = $target.title
    targetUrl = $target.url
    ok = $value.ok
    status = $value.status
    statusText = $value.statusText
    contentType = $value.contentType
    finalUrl = $value.finalUrl
    redirected = $value.redirected
    stage = $value.stage
    error = $value.error
}

$metadata |
    ConvertTo-Json -Depth 10 |
    Out-File (Join-Path $OutputDirectory "metadata.json") -Encoding utf8

if ($null -ne $value.body) {
    $extension = ".txt"
    if ($value.contentType -match "json") { $extension = ".json" }
    elseif ($value.contentType -match "html") { $extension = ".html" }
    elseif ($value.contentType -match "xml") { $extension = ".xml" }

    $safeName = ($ApiPath.Trim("/") -replace '[^A-Za-z0-9._-]', '_')
    if (-not $safeName) { $safeName = "root" }

    $bodyPath = Join-Path $OutputDirectory ($safeName + $extension)
    [IO.File]::WriteAllText($bodyPath, [string]$value.body, [Text.UTF8Encoding]::new($false))
    Write-Host "Respuesta guardada: $bodyPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "Estado HTTP: $($value.status) $($value.statusText)"
Write-Host "Content-Type: $($value.contentType)"
Write-Host "Redirigida: $($value.redirected)"

if (-not $value.ok) {
    Write-Host "La consulta no fue exitosa." -ForegroundColor Yellow
    if ($value.error) {
        Write-Host "Error: $($value.error)"
    }
}

Write-Host ""
Write-Host "Session Bridge finalizado." -ForegroundColor Green
