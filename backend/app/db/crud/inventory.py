from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import Inventory
from app.db.scheme.inventorys import InventoryUpdate, InventoryCreate


class InventoryCrud:

    @staticmethod
    async def get_by_id(db:AsyncSession, product_id:int | None = None,
                                         location_id:int | None = None) -> list[Inventory]:
        
        semiresult = select(Inventory)

        if product_id:
            semiresult = semiresult.filter(Inventory.product_id == product_id)
        if location_id:
            semiresult = semiresult.filter(Inventory.location_id == location_id)

        result = await db.execute(semiresult)

        return result.scalars.all()
    
    @staticmethod
    async def update_by_id(db:AsyncSession, inventory_id:int, inventory:InventoryUpdate) -> Inventory|None:
        db_inventory = await db.get(Inventory, inventory_id)
        if db_inventory:
            update_data = inventory.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_inventory, key, value)
            await db.flush()
            return db_inventory
        return None
    
    @staticmethod
    async def create(db:AsyncSession, user:InventoryCreate) -> Inventory:
        db_inventory=Inventory(**user.model_dump())
        db.add(db_inventory)
        await db.flush()
        return db_inventory
    
    @staticmethod
    async def delete(db: AsyncSession, inventory_id: int) -> Inventory | None:
        db_inventory = await db.get(Inventory, inventory_id)
        if db_inventory:
            await db.delete(db_inventory)
            await db.flush()
            return db_inventory
        return None