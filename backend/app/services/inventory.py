from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.db.models import Inventory

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