param(
    [string]$GameExecutable = "",
    [int]$TimeoutSeconds = 45
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
if ([string]::IsNullOrWhiteSpace($GameExecutable)) {
    $GameExecutable = Join-Path $repoRoot "bin\win64\Star Ruler 2.exe"
}
$GameExecutable = (Resolve-Path -LiteralPath $GameExecutable).Path

$tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
$profileRoot = Join-Path $tempRoot ("sr2-smoke-" + [guid]::NewGuid().ToString("N"))
$previousProfile = $env:STAR_RULER_2_PROFILE

try {
    New-Item -ItemType Directory -Path $profileRoot | Out-Null
    $env:STAR_RULER_2_PROFILE = $profileRoot

    $game = Start-Process `
        -FilePath $GameExecutable `
        -ArgumentList @("--mod", "our_scifi_mod", "--test-scripts", "--no-window", "--no-sound", "--no-steam", "--verbose") `
        -WorkingDirectory $repoRoot `
        -WindowStyle Hidden `
        -PassThru

    if (-not $game.WaitForExit($TimeoutSeconds * 1000)) {
        Stop-Process -Id $game.Id -Force
        throw "Headless script compilation exceeded $TimeoutSeconds seconds."
    }
    if ($game.ExitCode -ne 0) {
        throw "Headless script compilation exited with code $($game.ExitCode)."
    }

    $logPath = Join-Path $profileRoot "log.txt"
    if (-not (Test-Path -LiteralPath $logPath)) {
        throw "The engine did not create its test log at $logPath."
    }

    $log = Get-Content -LiteralPath $logPath -Raw
    foreach ($marker in @("Loading mod our_scifi_mod", "Server scripts:", "Client scripts:", "Shadow scripts:")) {
        if (-not $log.Contains($marker)) {
            throw "Engine smoke log is missing success marker: $marker"
        }
    }

    $failurePatterns = @(
        '(?im)^\s*Error(?:\s|:)',
        '(?i)Could not instantiate hook',
        '(?i)could not find inner hook',
        '(?i)not unlocked',
        '(?i)Exception'
    )
    foreach ($pattern in $failurePatterns) {
        if ($log -match $pattern) {
            $matchingLine = $log -split "`r?`n" |
                Where-Object { $_ -match $pattern } |
                Select-Object -First 1
            throw "Engine smoke log matched failure pattern '$pattern': $matchingLine"
        }
    }

    Write-Output "Headless engine smoke test passed."
}
finally {
    if ($null -eq $previousProfile) {
        Remove-Item Env:STAR_RULER_2_PROFILE -ErrorAction SilentlyContinue
    }
    else {
        $env:STAR_RULER_2_PROFILE = $previousProfile
    }

    if (Test-Path -LiteralPath $profileRoot) {
        $resolvedProfile = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $profileRoot).Path)
        $leaf = Split-Path -Leaf $resolvedProfile
        if (-not $resolvedProfile.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase) -or
            -not $leaf.StartsWith("sr2-smoke-", [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to clean unexpected smoke-test directory: $resolvedProfile"
        }
        Remove-Item -LiteralPath $resolvedProfile -Recurse -Force
    }
}
