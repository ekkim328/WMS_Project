from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class HistoryBase(BaseModel):
    event_type: str

    target_table: Optional[str] = None
    target_id: Optional[int] = None

    product_id: Optional[int] = None
    location_id: Optional[int] = None
    user_id: Optional[int] = None

    qty: Optional[int] = None
    before_qty: Optional[int] = None
    after_qty: Optional[int] = None

    status: str = "success"
    reason: Optional[str] = None


class HistoryCreate(HistoryBase):
    pass


class HistoryResponse(HistoryBase):
    history_id: int
    created_at: datetime

    class Config:
        from_attributes = True