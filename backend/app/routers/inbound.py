from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import get_current_username
from app.db.database import get_db
from app.db.scheme.inbounds import InboundRead, InboundCreate
from app.services import InboundService

router = APIRouter(prefix="/inbounds", tags=["Inbound"], dependencies=[Depends(get_current_username)])

@router.get("")
async def get_inbounds(product_id:int=Query(None), location_id:int=Query(None), db:AsyncSession=Depends(get_db)):
    return await InboundService.get_inbounds(db, product_id, location_id)

@router.post("", response_model=InboundRead)
async def create_inbound(inbound:InboundCreate, db:AsyncSession=Depends(get_db)):
    db_inbound = await InboundService.create(db, inbound)
    return db_inbound