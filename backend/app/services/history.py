from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.history import HistoryCrud
from app.db.scheme.histories import HistoryCreate


class HistoryService:

    @staticmethod
    async def record(
        db: AsyncSession,
        event_type: str,
        target_table: str | None = None,
        target_id: int | None = None,
        product_id: int | None = None,
        location_id: int | None = None,
        user_id: int | None = None,
        qty: int | None = None,
        before_qty: int | None = None,
        after_qty: int | None = None,
        status: str = "success",
        reason: str | None = None,
    ):
        history_data = HistoryCreate(
            event_type=event_type,
            target_table=target_table,
            target_id=target_id,
            product_id=product_id,
            location_id=location_id,
            user_id=user_id,
            qty=qty,
            before_qty=before_qty,
            after_qty=after_qty,
            status=status,
            reason=reason,
        )

        db_history = await HistoryCrud.create(db, history_data)

        return db_history