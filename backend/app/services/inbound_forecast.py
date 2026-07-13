import asyncio
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import HTTPException


class InboundForecastService:
    @staticmethod
    async def forecast_product(product_id: int):
        return await asyncio.to_thread(InboundForecastService._request_forecast, product_id)

    @staticmethod
    def _request_forecast(product_id: int):
        if os.getenv("AI_EMBEDDED", os.getenv("RENDER", "")).lower() in {
            "1", "true", "yes"
        }:
            from ai_forecast_server import InboundForecastModel

            return InboundForecastModel.forecast_product(product_id)

        base_url = os.getenv(
            "AI_INBOUND_FORECAST_URL",
            "http://127.0.0.1:8090/forecast/inbound",
        )
        separator = "&" if "?" in base_url else "?"
        ai_url = f"{base_url}{separator}{urlencode({'product_id': product_id})}"
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
                detail=f"AI inbound forecast server is unavailable: {exc.reason}",
            ) from exc
        except TimeoutError as exc:
            raise HTTPException(
                status_code=504,
                detail="AI inbound forecast server timed out.",
            ) from exc
