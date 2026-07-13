from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import get_current_username
from app.db.database import get_db
from app.services import InventoryService


router = APIRouter(prefix="/inventories", tags=["Inventory"], dependencies=[Depends(get_current_username)])

@router.get("")
async def get_inventories(product_id:int=Query(None), location_id:int=Query(None), db:AsyncSession=Depends(get_db)):
    return await InventoryService.get_inventorys(db, product_id, location_id)


@router.get("/location-options")
async def get_location_options(
    product_id: int = Query(..., ge=1),
    db: AsyncSession = Depends(get_db),
):
    return await InventoryService.get_location_options(db, product_id)
