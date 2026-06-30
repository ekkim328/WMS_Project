from pydantic import BaseModel, Field
from datetime import datetime


class OutboundBase(BaseModel):
    product_id:int
    location_id:int
    outbound_qty:int
    outbound_date:datetime

class OutboundCreate(BaseModel):
    product_id:int
    location_id:int
    outbound_qty:int=Field(ge=1)
    outbound_date:datetime | None = None

class OutboundUpdate(BaseModel):
    outbound_qty:int | None=None
    outbound_date:datetime | None=None

class OutboundInDB(OutboundBase):
    outbound_id: int

    class Config:
        from_attributes = True

class OutboundRead(OutboundInDB):
    pass


class OutboundForecastRead(BaseModel):
    predicted_qty: int
    predicted_qty_raw: float
    target_date: str
    based_on_date: str
    device: str
    basis: dict
