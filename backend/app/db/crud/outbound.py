from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import Outbound
from app.db.scheme.outbounds import OutboundCreate, OutboundUpdate

class OutboundCrud:
    @staticmethod
    async def create(db:AsyncSession, outbound:OutboundCreate) -> Outbound:
        db_outbound=Outbound(**outbound.model_dump())
        db.add(db_outbound)
        await db.flush()
        return db_outbound
    
    @staticmethod
    async def get_by_id(db:AsyncSession, product_id:int | None = None,
                                         location_id:int | None = None) -> list[Outbound]:
        
        semiresult = select(Outbound)

        if product_id:
            semiresult = semiresult.filter(Outbound.product_id == product_id)
        if location_id:
            semiresult = semiresult.filter(Outbound.location_id == location_id)

        result = await db.execute(semiresult)

        return result.scalars.all()