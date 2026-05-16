param(
    [string]$Revision = "head"
)

$ErrorActionPreference = "Stop"

if (-not $env:DATABASE_URL) {
    throw "DATABASE_URL must be set before running migrations."
}

if (-not $env:SECRET_KEY) {
    throw "SECRET_KEY must be set before running migrations."
}

alembic upgrade $Revision
