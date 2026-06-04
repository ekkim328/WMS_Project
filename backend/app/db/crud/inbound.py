from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import Inbound
from app.db.scheme.inbounds import InboundCreate, InboundUpdate


class InboundCrud:
    @staticmethod
    async def create(db:AsyncSession, inbound:InboundCreate) -> Inbound:
        db_inbound=Inbound(**inbound.model_dump())
        db.add(db_inbound)
        await db.flush()
        return db_inbound
    
    @staticmethod
    async def get_by_id(db:AsyncSession, product_id:int | None = None,
                                         location_id:int | None = None) -> list[Inbound]:
        
        semiresult = select(Inbound)

        if product_id:
            semiresult = semiresult.filter(Inbound.product_id == product_id)
        if location_id:
            semiresult = semiresult.filter(Inbound.location_id == location_id)

        result = await db.execute(semiresult)

        return result.scalars.all()