from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import get_current_username
from app.db.database import get_db
from app.db.scheme.outbounds import OutboundCreate, OutboundRead
from app.services import OutboundService


router = APIRouter(prefix="/outbounds", tags=["Outbound"], dependencies=[Depends(get_current_username)])

@router.get("")
async def get_outbounds(product_id:int=Query(None), location_id:int=Query(None), db:AsyncSession=Depends(get_db)):
    return await OutboundService.get_outbounds(db, product_id, location_id)

@router.post("", response_model=OutboundRead)
async def create_inbound(inbound:OutboundCreate, db:AsyncSession=Depends(get_db)):
    db_outbound = await OutboundService.create(db, inbound)
    return db_outbound