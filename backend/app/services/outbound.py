from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from app.db.models import Outbound, Inventory, Product
from app.db.scheme.outbounds import OutboundCreate
from app.db.crud import OutboundCrud, InventoryCrud
from app.services.history import HistoryService
from app.services.shortage import ShortageService


class OutboundService:
    @staticmethod
    async def get_outbounds(db: AsyncSession, product_id, location_id):
        query = select(Outbound, Product.product_name).join(
            Product,
            Outbound.product_id == Product.product_id,
        )

        if product_id:
            query = query.filter(Outbound.product_id == product_id)

        if location_id:
            query = query.filter(Outbound.location_id == location_id)

        query = query.order_by(Outbound.outbound_id.desc())

        result = await db.execute(query)
        return [
            {
                "outbound_id": outbound.outbound_id,
                "product_id": outbound.product_id,
                "product_name": product_name,
                "location_id": outbound.location_id,
                "outbound_qty": outbound.outbound_qty,
                "outbound_date": outbound.outbound_date,
            }
            for outbound, product_name in result.all()
        ]

    @staticmethod
    async def create(db: AsyncSession, outbound: OutboundCreate):
        try:
            query = (
                select(Inventory)
                .where(
                    Inventory.product_id == outbound.product_id,
                    Inventory.location_id == outbound.location_id,
                )
                .with_for_update()
            )

            result = await db.execute(query)
            db_inventory = result.scalar_one_or_none()

            if db_inventory and db_inventory.stock_qty > outbound.outbound_qty:
                db_inventory.stock_qty -= outbound.outbound_qty

            elif db_inventory and db_inventory.stock_qty == outbound.outbound_qty:
                await InventoryCrud.delete(db, db_inventory.inventory_id)

            else:
                available_qty = db_inventory.stock_qty if db_inventory else 0
                shortage_qty = outbound.outbound_qty - available_qty

                db_shortage = await ShortageService.create(
                    db=db,
                    product_id=outbound.product_id,
                    location_id=outbound.location_id,
                    requested_qty=outbound.outbound_qty,
                    available_qty=available_qty,
                    shortage_qty=shortage_qty,
                    reason="재고 부족으로 출고 실패"
                )

                await HistoryService.record(
                    db=db,
                    event_type="shortage",
                    target_table="shortages",
                    target_id=db_shortage.shortage_id,
                    product_id=outbound.product_id,
                    location_id=outbound.location_id,
                    qty=outbound.outbound_qty,
                    status="failed",
                    reason="재고 부족"
                )

                await db.commit()
                raise HTTPException(status_code=400, detail="재고가 부족함")

            db_outbound = await OutboundCrud.create(db, outbound)

            await HistoryService.record(
                db=db,
                event_type="outbound",
                target_table="outbounds",
                target_id=db_outbound.outbound_id,
                product_id=outbound.product_id,
                location_id=outbound.location_id,
                qty=outbound.outbound_qty,
                status="success",
                reason="출고 처리"
            )

            await db.commit()
            await db.refresh(db_outbound)

            return db_outbound

        except HTTPException:
            raise

        except Exception:
            await db.rollback()
            raise
