from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import History
from app.db.scheme.histories import HistoryCreate


class HistoryCrud:
    @staticmethod
    async def create(db: AsyncSession, history: HistoryCreate) -> History:
        db_history = History(**history.model_dump())
        db.add(db_history)
        await db.flush()
        return db_history

    @staticmethod
    async def get_by_target(
        db: AsyncSession,
        target_table: str | None = None,
        target_id: int | None = None,
    ) -> list[History]:

        semiresult = select(History)

        if target_table:
            semiresult = semiresult.filter(History.target_table == target_table)

        if target_id:
            semiresult = semiresult.filter(History.target_id == target_id)

        result = await db.execute(semiresult)

        return result.scalars().all()

    @staticmethod
    async def get_warnings(
        db: AsyncSession,
        product_id: int | None = None,
        location_id: int | None = None,
    ) -> list[History]:

        semiresult = select(History).filter(
            History.status.in_(["warning", "failed", "missing", "damaged", "delayed"])
        )

        if product_id:
            semiresult = semiresult.filter(History.product_id == product_id)

        if location_id:
            semiresult = semiresult.filter(History.location_id == location_id)

        result = await db.execute(semiresult)

        return result.scalars().all()