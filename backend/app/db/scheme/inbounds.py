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


class InboundLocationAlternative(BaseModel):
    location_id: int
    location_name: str | None = None
    zone: str | None = None
    score: float
    reason: str


class InboundLocationRecommendationRead(BaseModel):
    location_id: int
    location_name: str | None = None
    zone: str | None = None
    confidence: float
    score: float
    reason: str
    alternatives: list[InboundLocationAlternative] = []


class InboundForecastRead(BaseModel):
    product_id: int
    predicted_qty: int
    predicted_qty_raw: float
    target_date: str
    based_on_date: str
    device: str
    basis: dict
