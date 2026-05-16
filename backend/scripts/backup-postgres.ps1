param(
    [Parameter(Mandatory = $true)]
    [string]$DatabaseUrl,

    [string]$OutputDirectory = ".\backups"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command pg_dump -ErrorAction SilentlyContinue)) {
    throw "pg_dump was not found on PATH. Install PostgreSQL client tools on the backup host."
}

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupPath = Join-Path $OutputDirectory "field-sample-management-$timestamp.dump"

pg_dump --format=custom --no-owner --no-acl --file=$backupPath $DatabaseUrl
Write-Host "Backup written to $backupPath"
