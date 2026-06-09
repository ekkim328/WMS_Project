from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    barcode: str
    product_name: str
    category: str
    price: int


class ProductCreate(ProductBase):
    barcode: str = Field(max_length=30)
    product_name: str = Field(max_length=50)
    category: str = Field(max_length=40)
    price: int = Field(ge=0)


class ProductUpdate(BaseModel):
    barcode: str | None = Field(default=None, max_length=30)
    product_name: str | None = Field(default=None, max_length=50)
    category: str | None = Field(default=None, max_length=40)
    price: int | None = Field(default=None, ge=0)


class ProductRead(ProductBase):
    product_id: int

    class Config:
        from_attributes = True