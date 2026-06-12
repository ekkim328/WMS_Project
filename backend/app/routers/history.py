from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_username
from app.db.database import get_db
from app.db.scheme.histories import HistoryResponse
from app.db.crud.history import HistoryCrud


router = APIRouter(
    prefix="/history",
    tags=["History"],
    dependencies=[Depends(get_current_username)],
)


@router.get("/", response_model=list[HistoryResponse])
async def get_histories(
    product_id: int | None = None,
    location_id: int | None = None,
    db: AsyncSession = Depends(get_db)
):
    histories = await HistoryCrud.get_warnings(
        db=db,
        product_id=product_id,
        location_id=location_id
    )
    return histories


@router.get("/target", response_model=list[HistoryResponse])
async def get_history_by_target(
    target_table: str | None = None,
    target_id: int | None = None,
    db: AsyncSession = Depends(get_db)
):
    histories = await HistoryCrud.get_by_target(
        db=db,
        target_table=target_table,
        target_id=target_id
    )
    return histories
