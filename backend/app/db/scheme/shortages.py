from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ShortageCreate(BaseModel):
    product_id: int
    location_id: int
    requested_qty: int
    available_qty: int
    shortage_qty: int
    status: str = "unresolved"
    reason: Optional[str] = None


class ShortageRead(ShortageCreate):
    shortage_id: int
    created_at: datetime

    class Config:
        from_attributes = True