from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    product_name:str
    category:str
    price:int

class ProductCreate(BaseModel):
    product_name:str=Field(max_length=50)
    category:str=Field(max_length=40)
    price:int=Field(ge=0)

class ProductUpdate(BaseModel):
    product_name:str | None=None
    category:str | None=None
    price:int | None=None

class ProductInDB(ProductBase):
    product_id: int

    class Config:
        from_attributes = True

class ProductRead(ProductInDB):
    pass