Set-Location -Path $PSScriptRoot
& "C:\Users\hi\miniconda3\envs\torch_gpu\python.exe" -m uvicorn --app-dir backend ai_forecast_server:app --host 127.0.0.1 --port 8090
