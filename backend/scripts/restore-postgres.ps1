param(
    [Parameter(Mandatory = $true)]
    [string]$DatabaseUrl,

    [Parameter(Mandatory = $true)]
    [string]$BackupPath
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command pg_restore -ErrorAction SilentlyContinue)) {
    throw "pg_restore was not found on PATH. Install PostgreSQL client tools on the restore host."
}

if (-not (Test-Path $BackupPath)) {
    throw "Backup file not found: $BackupPath"
}

pg_restore --clean --if-exists --no-owner --no-acl --dbname=$DatabaseUrl $BackupPath
Write-Host "Restore completed from $BackupPath"
