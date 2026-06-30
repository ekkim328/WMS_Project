from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import get_current_username
from app.db.database import get_db
from app.db.scheme.inbounds import (
    InboundCreate,
    InboundForecastRead,
    InboundLocationRecommendationRead,
    InboundRead,
)
from app.services import InboundService
from app.services.inbound_forecast import InboundForecastService
from app.services.inbound_location_recommendation import InboundLocationRecommendationService

router = APIRouter(prefix="/inbounds", tags=["Inbound"], dependencies=[Depends(get_current_username)])

@router.get("")
async def get_inbounds(product_id:int=Query(None), location_id:int=Query(None), db:AsyncSession=Depends(get_db)):
    return await InboundService.get_inbounds(db, product_id, location_id)

@router.get("/forecast", response_model=InboundForecastRead)
async def get_inbound_forecast(product_id:int=Query(..., ge=1)):
    return await InboundForecastService.forecast_product(product_id)

@router.get("/location-recommendation", response_model=InboundLocationRecommendationRead)
async def get_inbound_location_recommendation(
    product_id:int=Query(..., ge=1),
    inbound_qty:int=Query(..., ge=1),
    db:AsyncSession=Depends(get_db),
):
    return await InboundLocationRecommendationService.recommend(db, product_id, inbound_qty)

@router.post("", response_model=InboundRead)
async def create_inbound(inbound:InboundCreate, db:AsyncSession=Depends(get_db)):
    db_inbound = await InboundService.create(db, inbound)
    return db_inbound
