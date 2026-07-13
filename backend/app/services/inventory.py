from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exists
from sqlalchemy.future import select
from fastapi import HTTPException
from app.db.models import Inventory, Location

class InventoryService:
    @staticmethod
    async def get_inventorys(db:AsyncSession, product_id, location_id):
        query = select(Inventory)
        if product_id:
            query = query.filter(Inventory.product_id==product_id)
        if location_id:
            query = query.filter(Inventory.location_id==location_id)
        query = query.order_by(Inventory.inventory_id.desc())
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_location_options(db: AsyncSession, product_id: int):
        stocked_result = await db.execute(
            select(Location, Inventory.stock_qty)
            .join(Inventory, Inventory.location_id == Location.location_id)
            .where(
                Inventory.product_id == product_id,
                Inventory.stock_qty > 0,
            )
            .order_by(Inventory.stock_qty.desc(), Location.location_name)
        )
        stocked_locations = stocked_result.all()

        if stocked_locations:
            return {
                "source": "product_stock",
                "items": [
                    {
                        "location_id": location.location_id,
                        "location_name": location.location_name,
                        "zone": location.zone,
                        "stock_qty": stock_qty,
                    }
                    for location, stock_qty in stocked_locations
                ],
            }

        empty_result = await db.execute(
            select(Location)
            .where(
                ~exists().where(Inventory.location_id == Location.location_id)
            )
            .order_by(Location.location_name)
        )
        empty_locations = empty_result.scalars().all()

        return {
            "source": "empty",
            "items": [
                {
                    "location_id": location.location_id,
                    "location_name": location.location_name,
                    "zone": location.zone,
                    "stock_qty": 0,
                }
                for location in empty_locations
            ],
        }
