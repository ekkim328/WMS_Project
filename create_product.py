import csv
import random

categories = {
    "음료": [
        "생수",
        "콜라",
        "사이다",
        "이온음료",
        "커피"
    ],
    "식품": [
        "햇반",
        "컵라면",
        "참치캔",
        "김치",
        "만두"
    ],
    "생활용품": [
        "샴푸",
        "린스",
        "바디워시",
        "치약",
        "칫솔"
    ],
    "전자제품": [
        "무선마우스",
        "키보드",
        "이어폰",
        "충전기",
        "USB"
    ]
}

rows = []

barcode = 8801000000000

for category, products in categories.items():
    for i in range(25):
        barcode += 1

        product_name = random.choice(products) + str(i)

        rows.append([
            barcode,
            product_name,
            category,
            random.randint(1000, 50000)
        ])

with open("products.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)

    writer.writerow([
        "barcode",
        "product_name",
        "category",
        "price"
    ])

    writer.writerows(rows)

print("완료")