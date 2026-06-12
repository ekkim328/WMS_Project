from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.shortage import ShortageCrud
from app.db.scheme.shortages import ShortageCreate


class ShortageService:

    @staticmethod
    async def create(
        db: AsyncSession,
        product_id: int,
        location_id: int,
        requested_qty: int,
        available_qty: int,
        shortage_qty: int,
        reason: str | None = None,
        status: str = "unresolved",
    ):
        shortage_data = ShortageCreate(
            product_id=product_id,
            location_id=location_id,
            requested_qty=requested_qty,
            available_qty=available_qty,
            shortage_qty=shortage_qty,
            status=status,
            reason=reason,
        )

        db_shortage = await ShortageCrud.create(db, shortage_data)

        return db_shortage