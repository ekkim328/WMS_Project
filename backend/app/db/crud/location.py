from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Location
from app.db.scheme.locations import LocationCreate, LocationUpdate

class LocationCrud:
    #로케이션 추가
    @staticmethod
    async def create_location(db:AsyncSession, location_data:LocationCreate) -> Location:
        new_location = Location(
            location_name = location_data.location_name,
            zone = location_data.zone
        )
        db.add(new_location)
        return new_location
    
    #로케이션 조회
    @staticmethod
    async def get_location_by_id(db:AsyncSession, location_id:int) -> Location|None:
        result = await db.execute(
            select(Location).where(Location.location_id == location_id)
        ) 
        return result.scalar_one_or_none()
    
    #이름, 존으로 조회
    @staticmethod
    async def get_location_by_name_zone(db:AsyncSession, location_name:str, zone:str) -> Location|None:
        result = await db.execute(
            select(Location).filter(Location.location_name==location_name)
            .filter(Location.zone==zone))
        return result.scalar_one_or_none()
    
    #로케이션 수정
    @staticmethod
    async def update_location(db:AsyncSession, db_location:Location, location_data:LocationUpdate) -> Location|None:
        if location_data.location_name is not None:
            db_location.location_name = location_data.location_name

        if location_data.zone is not None:
            db_location.zone = location_data.zone

        return db_location
    
    #로케이션 삭제
    @staticmethod
    async def delete_location_by_id(db:AsyncSession, location_id:int) -> Location|None:
        db_location = await db.get(Location, location_id)
        if db_location:
            await db.delete(db_location)
            await db.flush()
            return db_location
        return None
