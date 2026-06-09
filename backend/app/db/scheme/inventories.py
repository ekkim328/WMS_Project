from pydantic import BaseModel, Field


class InventoryBase(BaseModel):
    product_id:int
    location_id:int
    stock_qty:int

class InventoryCreate(BaseModel):
    product_id:int
    location_id:int
    stock_qty:int=Field(ge=0)

class InventoryUpdate(BaseModel):
    product_id:int | None = None
    location_id:int | None = None
    stock_qty:int | None = None

class InventoryInDB(InventoryBase):
    inventory_id:int
    
    class Config:
        from_attributes = True

class InventoryRead(InventoryInDB):
    pass