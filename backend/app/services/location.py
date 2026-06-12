from sqlalchemy import select
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.db.models import Location
from app.db.crud import LocationCrud
from app.db.scheme.locations import LocationCreate, LocationUpdate

class LocationService:
    async def create_location_service(db: AsyncSession, location_data: LocationCreate):
        try:
            stmt = select(Location).where(
                Location.location_name == location_data.location_name,
                Location.zone == location_data.zone
            )
            result = await db.execute(stmt)
            existing_location = result.scalar_one_or_none()

            if existing_location:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 로케이션입니다")
            new_location = await LocationCrud.create_location(db, location_data)
            await db.commit()
            await db.refresh(new_location)
            return new_location
        except HTTPException:
            raise
        except IntegrityError as exc:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 로케이션입니다",
            ) from exc

    async def get_location_by_id_service(db: AsyncSession, location_id: int):
        db_location = await LocationCrud.get_location_by_id(db, location_id)
        if not db_location:
            raise HTTPException(status_code=404, detail="Location not found")
        return db_location


    async def update_location_service(db: AsyncSession, location_id: int, location_data: LocationUpdate):
        db_location = await LocationCrud.get_location_by_id(db, location_id)
        if not db_location:
            raise HTTPException(status_code=404, detail="Location not found")
        updated_location = await LocationCrud.update_location(db, db_location, location_data)
        await db.commit()
        await db.refresh(updated_location)
        return updated_location


    async def delete_location_service(db: AsyncSession, location_id: int):
        try:
            db_location = await LocationCrud.delete_location_by_id(db, location_id)
            if not db_location:
                raise HTTPException(status_code=404, detail="Location not found")
            await db.commit()
            return db_location
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="사용 중인 로케이션은 삭제할 수 없습니다")
