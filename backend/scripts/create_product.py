import asyncio
import random
from backend.app.db.database import AsyncSessionLocal
from backend.app.db.models.products import Product
from app.db.database import AsyncSessionLocal
from app.db.models.products import Product

categories = {
    "음료": ["생수", "콜라", "사이다", "이온음료", "커피"],
    "식품": ["햇반", "컵라면", "참치캔", "김치", "만두"],
    "생활용품": ["샴푸", "린스", "바디워시", "치약", "칫솔"],
    "전자제품": ["무선마우스", "키보드", "이어폰", "충전기", "USB"]
}

async def main():
    async with AsyncSessionLocal() as session:
        barcode = 8801000000000

        for category, products in categories.items():
            for i in range(25):
                barcode += 1

                product = Product(
                    barcode=str(barcode),
                    product_name=random.choice(products) + str(i),
                    category=category,
                    price=random.randint(1000, 50000)
                )

                session.add(product)

        await session.commit()

    print("DB 상품 더미데이터 삽입 완료")

asyncio.run(main())