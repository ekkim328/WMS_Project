import asyncio
import json
import os
from datetime import datetime, timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Inbound, Inventory, Location, Outbound, Product, Shortage


class InboundLocationRecommendationService:
    @staticmethod
    async def recommend(db: AsyncSession, product_id: int, inbound_qty: int):
        if inbound_qty < 1:
            raise HTTPException(status_code=422, detail="inbound_qty must be greater than 0.")

        product = await db.get(Product, product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found.")

        locations = (await db.execute(select(Location).order_by(Location.location_id))).scalars().all()
        if not locations:
            raise HTTPException(status_code=422, detail="No locations are registered.")

        recent_since = datetime.utcnow() - timedelta(days=90)
        total_stock = await InboundLocationRecommendationService._sum_by_location(
            db,
            select(Inventory.location_id, func.coalesce(func.sum(Inventory.stock_qty), 0))
            .group_by(Inventory.location_id),
        )
        product_stock = await InboundLocationRecommendationService._sum_by_location(
            db,
            select(Inventory.location_id, func.coalesce(func.sum(Inventory.stock_qty), 0))
            .where(Inventory.product_id == product_id)
            .group_by(Inventory.location_id),
        )
        recent_outbound = await InboundLocationRecommendationService._sum_by_location(
            db,
            select(Outbound.location_id, func.coalesce(func.sum(Outbound.outbound_qty), 0))
            .where(Outbound.product_id == product_id, Outbound.outbound_date >= recent_since)
            .group_by(Outbound.location_id),
        )
        recent_inbound = await InboundLocationRecommendationService._sum_by_location(
            db,
            select(Inbound.location_id, func.coalesce(func.sum(Inbound.inbound_qty), 0))
            .where(Inbound.product_id == product_id, Inbound.inbound_date >= recent_since)
            .group_by(Inbound.location_id),
        )
        shortage_rows = await db.execute(
            select(
                Shortage.location_id,
                func.coalesce(func.sum(Shortage.shortage_qty), 0),
                func.count(Shortage.shortage_id),
            )
            .where(Shortage.product_id == product_id, Shortage.status == "unresolved")
            .group_by(Shortage.location_id)
        )
        shortages = {
            location_id: {"qty": int(qty or 0), "count": int(count or 0)}
            for location_id, qty, count in shortage_rows.all()
        }

        payload = {
            "product": {
                "product_id": product.product_id,
                "product_name": product.product_name,
                "category": product.category,
                "price": product.price,
            },
            "inbound_qty": inbound_qty,
            "candidates": [
                {
                    "location_id": location.location_id,
                    "location_name": location.location_name,
                    "zone": location.zone,
                    "same_product_stock": product_stock.get(location.location_id, 0),
                    "total_location_stock": total_stock.get(location.location_id, 0),
                    "recent_product_outbound_qty": recent_outbound.get(location.location_id, 0),
                    "recent_product_inbound_qty": recent_inbound.get(location.location_id, 0),
                    "unresolved_shortage_qty": shortages.get(location.location_id, {}).get("qty", 0),
                    "unresolved_shortage_count": shortages.get(location.location_id, {}).get("count", 0),
                }
                for location in locations
            ],
        }

        return await asyncio.to_thread(
            InboundLocationRecommendationService._request_recommendation,
            payload,
        )

    @staticmethod
    async def _sum_by_location(db: AsyncSession, query):
        rows = await db.execute(query)
        return {location_id: int(total or 0) for location_id, total in rows.all()}

    @staticmethod
    def _request_recommendation(payload):
        ai_url = os.getenv(
            "AI_INBOUND_LOCATION_URL",
            "http://127.0.0.1:8090/recommend/inbound-location",
        )
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            ai_url,
            data=body,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            method="POST",
        )

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
                detail=f"AI recommendation server is unavailable: {exc.reason}",
            ) from exc
        except TimeoutError as exc:
            raise HTTPException(
                status_code=504,
                detail="AI recommendation server timed out.",
            ) from exc
