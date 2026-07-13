import asyncio
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import HTTPException


class OutboundForecastService:
    @staticmethod
    async def forecast_today():
        return await asyncio.to_thread(OutboundForecastService._request_forecast)

    @staticmethod
    def _request_forecast():
        if os.getenv("AI_EMBEDDED", os.getenv("RENDER", "")).lower() in {
            "1", "true", "yes"
        }:
            from ai_forecast_server import OutboundForecastModel

            return OutboundForecastModel.forecast_today()

        ai_url = os.getenv(
            "AI_OUTBOUND_FORECAST_URL",
            "http://127.0.0.1:8090/forecast/outbound/today",
        )
        request = Request(ai_url, headers={"Accept": "application/json"})

        try:
            with urlopen(request, timeout=5) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.reason
            try:
                payload = json.loads(exc.read().decode("utf-8"))
                detail = payload.get("detail", detail)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
            raise HTTPException(status_code=exc.code, detail=detail) from exc
        except URLError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"AI forecast server is unavailable: {exc.reason}",
            ) from exc
        except TimeoutError as exc:
            raise HTTPException(
                status_code=504,
                detail="AI forecast server timed out.",
            ) from exc
