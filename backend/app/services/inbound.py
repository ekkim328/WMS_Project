from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.db.models import Inbound
from app.db.models import Inventory
from app.db.scheme.inbounds import InboundCreate, InboundRead, InboundUpdate
from app.db.scheme.inventorys import InventoryUpdate, InventoryCreate
from app.db.crud import InboundCrud, InventoryCrud


class InboundService:
    
    @staticmethod
    async def get_inbounds(db:AsyncSession, product_id, location_id):
        query = select(Inbound)
        if product_id:
            query = query.filter(Inbound.product_id==product_id)
        if location_id:
            query = query.filter(Inbound.location_id==location_id)
        query = query.order_by(Inbound.inbound_id.desc())
        result = await db.execute(query)
        return result.scalars().all()



    @staticmethod # 재고 테이블에서 product_id, location_id로 가져옴
    async def create(db:AsyncSession, inbound:InboundCreate):
        query = select(Inventory)
        query = query.filter(Inventory.product_id == inbound.product_id)
        query = query.filter(Inventory.location_id == inbound.location_id)
        result = await db.execute(query)
        db_inventory = result.scalars().first()

        if db_inventory: #데이터가 있으면 기존 inventory 데이터의 개수에 입고/출고하는 개수 계산해서 다시 넣어줌
            db_inventory.stock_qty += inbound.inbound_qty
        else: #입고의 경우 데이터가 없으면 create로 넣어줌
            new_inventory= InventoryCreate(product_id = inbound.product_id,
                                    location_id = inbound.location_id,
                                    stock_qty = inbound.inbound_qty)
            
            db_inventory=await InventoryCrud.create(db,new_inventory)
                
        db_inbound = await InboundCrud.create(db, inbound)
    
        await db.commit()
        await db.refresh(db_inbound)
        return db_inbound

