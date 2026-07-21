$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

$aiPythonPath = $env:WMS_AI_PYTHON
if ($aiPythonPath) {
    & $aiPythonPath -m uvicorn --app-dir backend ai_forecast_server:app --host 127.0.0.1 --port 8090
    exit $LASTEXITCODE
}

$aiCondaEnvironment = if ($env:WMS_AI_CONDA_ENV) { $env:WMS_AI_CONDA_ENV } else { "torch_gpu" }
$condaCommand = Get-Command conda -ErrorAction SilentlyContinue

if (-not $condaCommand) {
    throw "AI 실행 환경을 찾지 못했습니다. WMS_AI_PYTHON에 AI 의존성이 설치된 Python 경로를 지정해 주세요."
}

& conda run -n $aiCondaEnvironment python -m uvicorn --app-dir backend ai_forecast_server:app --host 127.0.0.1 --port 8090
exit $LASTEXITCODE
