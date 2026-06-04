from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import get_current_username
from app.db.database import get_db
from app.db.scheme.locations import LocationCreate, LocationUpdate, LocationRead
from app.services.location import LocationService

router = APIRouter(prefix="/locations", tags=["Location"], dependencies=[Depends(get_current_username)])

#로케이션 추가
@router.post("/locations", response_model=LocationCreate)
async def create_location(location_data:LocationCreate, db:AsyncSession = Depends(get_db)):
    return await LocationService.create_location_service(db, location_data)

#로케이션 단건 조회
@router.get("/location/{location_id}", response_model=LocationRead)
async def get_location_by_id(location_id:int, db:AsyncSession = Depends(get_db)):
    return await LocationService.get_location_by_id_service(db,location_id)

#로케이션 수정
@router.put("/location/{location_id}", response_model=LocationUpdate)
async def update_location(location_id:int, location_data:LocationUpdate,db:AsyncSession=Depends(get_db)):
    return await LocationService.update_location_service(db, location_id, location_data)

#로케이션 삭제
@router.delete("/location/{location_id}")
async def delete_location(location_id:int, db:AsyncSession = Depends(get_db)):
    return await LocationService.delete_location_service(db, location_id)