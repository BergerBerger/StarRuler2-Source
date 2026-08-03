param(
    [string]$GameExecutable = "",
    [int]$ObservationSeconds = 20
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
if ([string]::IsNullOrWhiteSpace($GameExecutable)) {
    $GameExecutable = Join-Path $repoRoot "bin\win64\Star Ruler 2.exe"
}
$GameExecutable = (Resolve-Path -LiteralPath $GameExecutable).Path

$tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
$profileRoot = Join-Path $tempRoot ("sr2-quickstart-" + [guid]::NewGuid().ToString("N"))
$previousProfile = $env:STAR_RULER_2_PROFILE
$game = $null

try {
    New-Item -ItemType Directory -Path $profileRoot | Out-Null
    $env:STAR_RULER_2_PROFILE = $profileRoot

    $game = Start-Process `
        -FilePath $GameExecutable `
        -ArgumentList @("--mod", "our_scifi_mod", "--quickstart", "--no-sound", "--no-steam", "--verbose") `
        -WorkingDirectory $repoRoot `
        -WindowStyle Hidden `
        -PassThru

    $exited = $game.WaitForExit($ObservationSeconds * 1000)
    if (-not $exited) {
        Stop-Process -Id $game.Id -Force
        $game.WaitForExit()
    }
    elseif ($game.ExitCode -ne 0) {
        throw "Quick-start exited with code $($game.ExitCode)."
    }

    $logPath = Join-Path $profileRoot "log.txt"
    if (-not (Test-Path -LiteralPath $logPath)) {
        throw "The engine did not create its quick-start log at $logPath."
    }
    $log = Get-Content -LiteralPath $logPath -Raw

    foreach ($marker in @("Loading mod our_scifi_mod", "Map generation:", "Finished computing hulls")) {
        if (-not $log.Contains($marker)) {
            throw "Quick-start log is missing success marker: $marker"
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
            throw "Quick-start log matched failure pattern '$pattern': $matchingLine"
        }
    }

    Write-Output "Quick-start smoke test passed."
}
finally {
    if ($null -ne $game -and -not $game.HasExited) {
        Stop-Process -Id $game.Id -Force
    }
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
            -not $leaf.StartsWith("sr2-quickstart-", [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to clean unexpected quick-start directory: $resolvedProfile"
        }
        Remove-Item -LiteralPath $resolvedProfile -Recurse -Force
    }
}
