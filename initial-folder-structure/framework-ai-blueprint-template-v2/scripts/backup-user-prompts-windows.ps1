#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Backup VS Code user prompts (Windows) into this template's github-config directory.
# Safe behavior:
# - Resolves paths from this script location (independent of current working directory)
# - Deletes only contents of backup-prompts directory, not the directory itself
# - Guards against unexpected target paths before any destructive operation

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TargetDir = Join-Path (Split-Path $ScriptDir -Parent) "user-prompts-content"
$SourceDir = Join-Path $env:APPDATA "Code\User\prompts"

if (-not (Test-Path $SourceDir -PathType Container)) {
    Write-Error "ERROR: Source prompts directory does not exist: $SourceDir"
    exit 1
}

# Normalize for comparison
$SourceDir = (Resolve-Path $SourceDir).Path

if ($SourceDir -eq $TargetDir) {
    Write-Error "ERROR: Source and target directories are the same path. Aborting."
    exit 1
}

# Guard against accidental broad deletions
if ($TargetDir -notmatch [regex]::Escape("framework-ai-blueprint-template-v2\user-prompts-content")) {
    Write-Error "ERROR: Refusing to operate on unexpected target path: $TargetDir"
    exit 1
}

Write-Host "Source: $SourceDir"
Write-Host "Target: $TargetDir"

# Ensure target directory exists
if (-not (Test-Path $TargetDir -PathType Container)) {
    New-Item -ItemType Directory -Path $TargetDir | Out-Null
}

Write-Host "Clearing target contents..."
Get-ChildItem -Path $TargetDir -Force | Remove-Item -Recurse -Force

Write-Host "Copying prompts folder into target..."
Copy-Item -Path "$SourceDir\*" -Destination $TargetDir -Recurse -Force

$SourceCount = (Get-ChildItem -Path $SourceDir -Recurse -File).Count
$TargetCount = (Get-ChildItem -Path $TargetDir -Recurse -File).Count

Write-Host "Done."
Write-Host "Source files: $SourceCount"
Write-Host "Target files: $TargetCount"
Write-Host "Backup location: $TargetDir"
