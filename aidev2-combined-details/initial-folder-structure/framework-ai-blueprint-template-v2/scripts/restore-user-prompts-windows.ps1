#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Restore VS Code user prompts (Windows) from this template's github-config/backup-prompts.
# Safe behavior:
# - Copies backup prompts INTO the VS Code user prompts folder (additive/merge only)
# - Does NOT delete any prompts that already exist in the VS Code user prompts folder
# - Existing files with the same name will be overwritten with the backed-up version

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceDir = (Resolve-Path (Join-Path $ScriptDir "..\user-prompts-content")).Path

# User-level VS Code prompts folder
$TargetDir = Join-Path $env:APPDATA "Code\User\prompts"
Write-Host "Resolved VS Code prompts location: $TargetDir"

if (-not (Test-Path $SourceDir -PathType Container)) {
    Write-Error "ERROR: Backup prompts directory does not exist: $SourceDir"
    exit 1
}

# Guard against restoring from unexpected source path
if ($SourceDir -notmatch [regex]::Escape("framework-ai-blueprint-template-v2\user-prompts-content")) {
    Write-Error "ERROR: Refusing to restore from unexpected source path: $SourceDir"
    exit 1
}

# Create VS Code prompts folder if it does not exist
if (-not (Test-Path $TargetDir -PathType Container)) {
    Write-Host "Creating VS Code prompts directory: $TargetDir"
    New-Item -ItemType Directory -Path $TargetDir | Out-Null
}

Write-Host "Source (backup): $SourceDir"
Write-Host "Target (VS Code prompts): $TargetDir"
Write-Host "Restoring prompts (merge - no deletions)..."

# Copy all files from backup into VS Code prompts folder.
# Existing files in the target that are NOT in the backup are left untouched.
Get-ChildItem -Path $SourceDir -Recurse -File | ForEach-Object {
    $RelativePath = $_.FullName.Substring($SourceDir.Length).TrimStart('\')
    $DestFile = Join-Path $TargetDir $RelativePath
    $DestFolder = Split-Path $DestFile -Parent

    if (-not (Test-Path $DestFolder -PathType Container)) {
        New-Item -ItemType Directory -Path $DestFolder | Out-Null
    }

    Copy-Item -Path $_.FullName -Destination $DestFile -Force
    Write-Host "  Restored: $RelativePath"
}

$SourceCount = (Get-ChildItem -Path $SourceDir -Recurse -File).Count
$TargetCount = (Get-ChildItem -Path $TargetDir -Recurse -File).Count

Write-Host "Done."
Write-Host "Files restored from backup: $SourceCount"
Write-Host "Total files now in VS Code prompts: $TargetCount"
Write-Host "Restore location: $TargetDir"
