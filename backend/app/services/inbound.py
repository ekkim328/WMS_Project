from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.future import select
from app.db.models import Inbound
from app.db.models import Inventory
from app.db.scheme.inbounds import InboundCreate
from app.db.crud import InboundCrud
from app.services.history import HistoryService


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



    @staticmethod
    async def create(db: AsyncSession, inbound: InboundCreate):
        try:
            inventory_upsert = mysql_insert(Inventory).values(
                product_id=inbound.product_id,
                location_id=inbound.location_id,
                stock_qty=inbound.inbound_qty,
            )
            inventory_upsert = inventory_upsert.on_duplicate_key_update(
                stock_qty=Inventory.stock_qty + inbound.inbound_qty
            )
            await db.execute(inventory_upsert)

            db_inbound = await InboundCrud.create(db, inbound)

            await HistoryService.record(
                db=db,
                event_type="inbound",
                target_table="inbounds",
                target_id=db_inbound.inbound_id,
                product_id=inbound.product_id,
                location_id=inbound.location_id,
                qty=inbound.inbound_qty,
                status="success",
                reason="입고 처리",
            )

            await db.commit()
            await db.refresh(db_inbound)
            return db_inbound
        except Exception:
            await db.rollback()
            raise

