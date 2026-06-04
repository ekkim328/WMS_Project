from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import get_current_username
from app.db.database import get_db
from app.db.scheme.products import ProductCreate,ProductUpdate,ProductRead
from app.services.product import ProductService

router = APIRouter(prefix="/products", tags=["Product"], dependencies=[Depends(get_current_username)])

#상품 추가
@router.post("/products", response_model=ProductCreate)
async def create_product(product:ProductCreate,db:AsyncSession = Depends(get_db)):
    db_product=ProductService.create_product_service(db,product)
    return await db_product

#상품 전체 조회
@router.get("/products", response_model=list[ProductRead])
async def get_all_products(db:AsyncSession = Depends(get_db)):
    return await ProductService.get_all_products_service(db)

#상품 단건 조회
@router.get("/products/{product_id}", response_model=ProductRead)
async def get_product_by_id(product_id : int, db:AsyncSession = Depends(get_db)):
    return await ProductService.get_product_by_id_service(db,product_id)

#상품 수정
@router.put("/product/{product_id}")
async def update_product(product_id:int, product_data : ProductUpdate, db:AsyncSession = Depends(get_db)):
    return await ProductService.update_product_service(db, product_id,product_data)

#상품 삭제
@router.delete("/product/{product_id}")
async def delete_product(product_id:int, db:AsyncSession = Depends(get_db)):
    return await ProductService.delete_product_service(db, product_id)