import asyncio
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parents[2]
TRUE_VALUES = {"1", "true", "yes"}
FALSE_VALUES = {"0", "false", "no"}
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _is_true(value: str | None) -> bool:
    return (value or "").lower() in TRUE_VALUES


def _should_auto_start() -> bool:
    if _is_true(os.getenv("RENDER")):
        return False

    embedded_value = os.getenv("AI_EMBEDDED", os.getenv("RENDER", ""))
    if _is_true(embedded_value):
        return False

    auto_start_value = os.getenv("AI_AUTO_START_LOCAL", "true").lower()
    if auto_start_value in FALSE_VALUES:
        return False

    forecast_url = os.getenv(
        "AI_OUTBOUND_FORECAST_URL",
        "http://127.0.0.1:8090/forecast/outbound/today",
    )
    return urlsplit(forecast_url).hostname in LOCAL_HOSTS


def _health_url() -> str:
    configured_url = os.getenv("AI_HEALTH_URL")
    if configured_url:
        return configured_url

    forecast_url = os.getenv(
        "AI_OUTBOUND_FORECAST_URL",
        "http://127.0.0.1:8090/forecast/outbound/today",
    )
    parsed = urlsplit(forecast_url)
    return f"{parsed.scheme}://{parsed.netloc}/health"


def _check_health(url: str) -> bool:
    try:
        request = Request(url, headers={"Accept": "application/json"})
        with urlopen(request, timeout=1) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload.get("status") == "ok"
    except (OSError, URLError, json.JSONDecodeError, UnicodeDecodeError):
        return False


def _python_has_ai_dependencies(python_path: str) -> bool:
    result = subprocess.run(
        [python_path, "-c", "import numpy, pandas"],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    return result.returncode == 0


def _resolve_ai_python() -> str:
    configured_python = os.getenv("WMS_AI_PYTHON")
    if configured_python:
        python_path = str(Path(configured_python).expanduser().resolve())
        if not Path(python_path).is_file():
            raise RuntimeError(f"WMS_AI_PYTHON 경로를 찾을 수 없습니다: {python_path}")
        return python_path

    if _python_has_ai_dependencies(sys.executable):
        return sys.executable

    conda_command = shutil.which("conda")
    if not conda_command:
        raise RuntimeError(
            "AI Python 환경을 찾을 수 없습니다. WMS_AI_PYTHON을 지정해 주세요."
        )

    conda_environment = os.getenv("WMS_AI_CONDA_ENV", "torch_gpu")
    result = subprocess.run(
        [
            conda_command,
            "run",
            "-n",
            conda_environment,
            "python",
            "-c",
            "import sys; print(sys.executable)",
        ],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Conda AI 환경을 실행할 수 없습니다: {conda_environment}"
        )

    candidates = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not candidates or not Path(candidates[-1]).is_file():
        raise RuntimeError(
            f"Conda AI 환경의 Python 경로를 확인할 수 없습니다: {conda_environment}"
        )
    return candidates[-1]


async def start_local_ai_server():
    if not _should_auto_start():
        return None

    health_url = _health_url()
    if await asyncio.to_thread(_check_health, health_url):
        logger.info("기존 로컬 AI 서버를 사용합니다: %s", health_url)
        return None

    try:
        ai_python = await asyncio.to_thread(_resolve_ai_python)
    except (OSError, subprocess.SubprocessError, RuntimeError) as exc:
        logger.warning("로컬 AI 서버 자동 시작을 건너뜁니다: %s", exc)
        return None

    parsed_health_url = urlsplit(health_url)
    host = parsed_health_url.hostname or "127.0.0.1"
    port = parsed_health_url.port or 8090
    process_options = {
        "cwd": str(BACKEND_DIR),
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "nt":
        process_options["creationflags"] = subprocess.CREATE_NO_WINDOW

    process = await asyncio.to_thread(
        subprocess.Popen,
        [
            ai_python,
            "-m",
            "uvicorn",
            "ai_forecast_server:app",
            "--host",
            host,
            "--port",
            str(port),
        ],
        **process_options,
    )

    for _ in range(30):
        if await asyncio.to_thread(_check_health, health_url):
            logger.info("로컬 AI 서버가 준비되었습니다: %s", health_url)
            return process
        if process.poll() is not None:
            logger.warning("로컬 AI 서버가 시작 중 종료되었습니다.")
            return None
        await asyncio.sleep(0.5)

    await stop_local_ai_server(process)
    logger.warning("로컬 AI 서버가 제한 시간 안에 준비되지 않았습니다.")
    return None


async def stop_local_ai_server(process) -> None:
    if process is None or process.poll() is not None:
        return

    process.terminate()
    try:
        await asyncio.to_thread(process.wait, timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        await asyncio.to_thread(process.wait)
