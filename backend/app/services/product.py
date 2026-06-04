from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.db.models import Product
from app.db.crud.product import ProductCrud
from app.db.scheme.products import ProductCreate, ProductUpdate

class ProductService:
    async def create_product_service(db: AsyncSession, product_data: ProductCreate):
        stmt = select(Product).where(
            Product.product_name == product_data.product_name,
            Product.category == product_data.category
        )
        result = await db.execute(stmt)
        existing_product = result.scalar_one_or_none()

        if existing_product:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 상품입니다")
        new_product = await ProductCrud.create_product(db, product_data)
        await db.commit()
        await db.refresh(new_product)
        return new_product


    async def get_all_products_service(db: AsyncSession):
        return await ProductCrud.get_all_products(db)


    async def get_product_by_id_service(db: AsyncSession, product_id: int):
        db_product = await ProductCrud.get_product_by_id(db, product_id)
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        return db_product


    async def update_product_service(db: AsyncSession, product_id: int, product_data: ProductUpdate):
        db_product = await ProductCrud.get_product_by_id(db, product_id)

        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        updated_product = await ProductCrud.update_product(db, db_product, product_data)
        await db.commit()
        await db.refresh(updated_product)
        return updated_product


    async def delete_product_service(db: AsyncSession, product_id: int):
        try:
            db_product = await ProductCrud.delete_product_by_id(db, product_id)
            if not db_product:
                raise HTTPException(status_code=404, detail="Product not found")
            await db.commit()
            return db_product
        except IntegrityError:
            raise HTTPException(status_code=400, detail="해당 상품은 삭제할 수 없습니다")
        