from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Shortage
from app.db.scheme.shortages import ShortageCreate


class ShortageCrud:

    @staticmethod
    async def create(db: AsyncSession, shortage: ShortageCreate) -> Shortage:
        db_shortage = Shortage(**shortage.model_dump())

        db.add(db_shortage)
        await db.flush()

        return db_shortage