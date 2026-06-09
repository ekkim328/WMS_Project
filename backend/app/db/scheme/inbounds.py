from pydantic import BaseModel, Field
from datetime import datetime


class InboundBase(BaseModel):
    product_id:int
    location_id:int
    inbound_qty:int
    inbound_date:datetime

class InboundCreate(BaseModel):
    product_id:int
    location_id:int
    inbound_qty:int=Field(ge=1)
    inbound_date:datetime | None = None

class InboundUpdate(BaseModel):
    inbound_qty:int | None=None
    inbound_date:datetime | None=None

class InboundInDB(InboundBase):
    inbound_id: int

    class Config:
        from_attributes = True

class InboundRead(InboundInDB):
    pass