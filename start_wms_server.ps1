$ErrorActionPreference = "Stop"

Set-Location -Path (Join-Path $PSScriptRoot "backend")
conda run -n fastapi uvicorn main:app --host 127.0.0.1 --port 8081
