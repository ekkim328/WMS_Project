from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.products import Product
from app.db.scheme.products import ProductCreate, ProductUpdate

class ProductCrud:
    #상품 추가
    @staticmethod
    async def create_product(db:AsyncSession, product_data:ProductCreate):
        new_product = Product(
            product_name=product_data.product_name,
            category = product_data.category,
            price = product_data.price
        )
        db.add(new_product)
        return new_product

    
    #상품 전체 조회
    @staticmethod
    async def get_all_products(db:AsyncSession):
        result = await db.execute(select(Product))
        return result.scalars().all()
    
    #상품 단건 조회
    @staticmethod
    async def get_product_by_id(db:AsyncSession,product_id:int):
        result = await db.execute(
            select(Product).where(Product.product_id == product_id)
        )
        return result.scalar_one_or_none()
    
    #상품 수정
    @staticmethod
    async def update_product(db:AsyncSession, db_product:Product, product_data:ProductUpdate):
        if product_data.product_name is not None:
            db_product.product_name = product_data.product_name

        if product_data.category is not None:
            db_product.category = product_data.category

        if product_data.price is not None:
            db_product.price = product_data.price

        return db_product
    #상품 삭제
    @staticmethod
    async def delete_product_by_id(db:AsyncSession, product_id:int):
        db_product = await db.get(Product, product_id)
        if db_product:
            await db.delete(db_product)
            await db.flush()
            return db_product
        return None