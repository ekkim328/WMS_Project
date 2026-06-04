from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.db.models import Outbound
from app.db.scheme.outbounds import OutboundCreate, OutboundRead
from app.db.crud import OutboundCrud, InventoryCrud
from app.db.models import Inventory

class OutboundService:
    @staticmethod
    async def get_outbounds(db:AsyncSession, product_id, location_id):
        query = select(Outbound)
        if product_id:
            query = query.filter(Outbound.product_id==product_id)
        if location_id:
            query = query.filter(Outbound.location_id==location_id)
        query = query.order_by(Outbound.outbound_id.desc())
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create(db:AsyncSession, outbound_create:OutboundCreate) -> OutboundRead:
        try:
            db_outbound = await OutboundCrud.create(db, outbound_create)
            # 재고 테이블에서 product_id, location_id로 불러옴
            # 있으면 개수 체크
            # 재고 개수가 출고 개수보다 많으면 업데이트
            # 재고 개수 = 출고 개수면 삭제
            # 부족하거나 테이블에 없으면 raise
            #인풋값이 삭제 or 업데이트 or 개수안맞으면 에러
            await db.commit()
            await db.refresh(db_outbound)
            return db_outbound
        except:
            await db.rollback()
            raise

    @staticmethod # 재고 테이블에서 product_id, location_id로 가져옴
    async def create(db:AsyncSession, outbound:OutboundCreate):
        query = select(Inventory)
        query = query.filter(Inventory.product_id == outbound.product_id)
        query = query.filter(Inventory.location_id == outbound.location_id)
        result = await db.execute(query)
        db_inventory = result.scalars().first()

        if db_inventory and db_inventory.stock_qty > outbound.outbound_qty: #데이터가 있으면 기존 inventory 데이터의 개수에 입고/출고하는 개수 계산해서 다시 넣어줌
            db_inventory.stock_qty -= outbound.outbound_qty
        elif db_inventory and db_inventory.stock_qty == outbound.outbound_qty:
            await InventoryCrud.delete(db, db_inventory.inventory_id)
        else:
            raise HTTPException(status_code=400, detail="재고가 부족함")

        db_outbound = await OutboundCrud.create(db, outbound)

        await db.commit()
        await db.refresh(db_outbound)
        return db_outbound