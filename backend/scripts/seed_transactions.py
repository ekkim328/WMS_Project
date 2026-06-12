# backend/app/routers/admin_seed.py

import random
from collections import Counter
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_username
from app.db.database import get_db

from app.db.models.products import Product
from app.db.models.locations import Location

# 만약 여기서 에러 나면 inventories -> inventorys 로 바꾸기
from app.db.models.inventories import Inventory

from app.db.scheme.inbounds import InboundCreate
from app.db.scheme.outbounds import OutboundCreate

from app.services.inbound import InboundService
from app.services.outbound import OutboundService
from app.services.shortage import ShortageService
from app.services.history import HistoryService


router = APIRouter(
    prefix="/admin/seed",
    tags=["Admin Seed"],
    dependencies=[Depends(get_current_username)],
)


PRODUCT_CATEGORIES = [
    "화장품",
    "식품",
    "생활용품",
    "전자제품",
    "패션",
    "문구",
    "반려동물",
    "건강용품",
]


SHORTAGE_REASON_WEIGHTS = [
    ("재고 부족", 0.45),
    ("상품 파손", 0.15),
    ("오피킹", 0.12),
    ("스캔 오류", 0.10),
    ("로케이션 불일치", 0.08),
    ("입고 지연", 0.07),
    ("바코드 불일치", 0.03),
]


def weighted_shortage_reason() -> str:
    reasons, weights = zip(*SHORTAGE_REASON_WEIGHTS)
    return random.choices(reasons, weights=weights, k=1)[0]


def random_date(start_date: datetime, days: int) -> datetime:
    date = start_date + timedelta(days=random.randint(0, days))
    hour = random.randint(8, 22)
    minute = random.randint(0, 59)
    return date.replace(hour=hour, minute=minute)


def choose_product(product_count: int) -> int:
    popular_products = list(range(1, min(10, product_count) + 1))

    if popular_products and random.random() < 0.45:
        return random.choice(popular_products)

    return random.randint(1, product_count)


class SeedShortageCreate(BaseModel):
    product_id: int
    location_id: int
    requested_qty: int
    available_qty: int
    shortage_qty: int
    status: str = "unresolved"
    reason: str
    created_at: Optional[datetime] = None


@router.post("/products")
async def seed_products(
    count: int = Query(100, ge=1),
    db: AsyncSession = Depends(get_db),
):
    created = 0
    skipped = 0

    result = await db.execute(select(Product.product_id))
    existing_ids = set(result.scalars().all())

    for product_id in range(1, count + 1):
        if product_id in existing_ids:
            skipped += 1
            continue

        category = random.choice(PRODUCT_CATEGORIES)

        product = Product(
            product_id=product_id,
            barcode=f"880000000{product_id:05d}",
            product_name=f"{category} 상품 {product_id:03d}",
            category=category,
            price=random.randint(1000, 100000),
        )

        db.add(product)
        created += 1

    await db.commit()

    return {
        "message": "상품 더미데이터 생성 완료",
        "created": created,
        "skipped": skipped,
    }


@router.post("/locations")
async def seed_locations(
    db: AsyncSession = Depends(get_db),
):
    created = 0
    skipped = 0

    result = await db.execute(select(Location.location_id))
    existing_ids = set(result.scalars().all())

    zones = ["A", "B", "C", "D"]
    location_id = 1

    for zone in zones:
        for rack in range(1, 6):
            for slot in range(1, 11):
                if location_id in existing_ids:
                    skipped += 1
                    location_id += 1
                    continue

                location = Location(
                    location_id=location_id,
                    location_name=f"{zone}-{rack:02d}-{slot:02d}",
                    zone=zone,
                )

                db.add(location)
                created += 1
                location_id += 1

    await db.commit()

    return {
        "message": "로케이션 더미데이터 생성 완료",
        "created": created,
        "skipped": skipped,
        "total_location_count": 200,
    }


@router.post("/initial-stock")
async def seed_initial_stock(
    product_count: int = Query(100, ge=1),
    location_count: int = Query(200, ge=1),
    db: AsyncSession = Depends(get_db),
):
    created = 0
    failed = 0
    errors = []

    for product_id in range(1, product_count + 1):
        selected_locations = random.sample(
            range(1, location_count + 1),
            random.randint(2, 4),
        )

        for location_id in selected_locations:
            qty = random.randint(300, 900)

            inbound_data = InboundCreate(
                product_id=product_id,
                location_id=location_id,
                inbound_qty=qty,
                inbound_date=datetime(2025, 1, 1, 9, 0),
            )

            try:
                await InboundService.create(db, inbound_data)
                created += 1
            except Exception as e:
                await db.rollback()
                failed += 1

                if len(errors) < 10:
                    errors.append(str(e)[:200])

    return {
        "message": "초기 재고 생성 완료",
        "created": created,
        "failed": failed,
        "errors": errors,
    }


@router.post("/shortage")
async def seed_shortage(
    shortage: SeedShortageCreate,
    db: AsyncSession = Depends(get_db),
):
    db_shortage = await ShortageService.create(
        db=db,
        product_id=shortage.product_id,
        location_id=shortage.location_id,
        requested_qty=shortage.requested_qty,
        available_qty=shortage.available_qty,
        shortage_qty=shortage.shortage_qty,
        status=shortage.status,
        reason=shortage.reason,
    )

    await HistoryService.record(
        db=db,
        event_type="shortage",
        target_table="shortages",
        target_id=db_shortage.shortage_id,
        product_id=shortage.product_id,
        location_id=shortage.location_id,
        qty=shortage.requested_qty,
        status="failed",
        reason=shortage.reason,
    )

    await db.commit()
    await db.refresh(db_shortage)

    return {
        "message": "미출 더미데이터 생성 완료",
        "shortage_id": db_shortage.shortage_id,
        "reason": shortage.reason,
    }


async def create_random_shortage(
    db: AsyncSession,
    product_id: int,
    location_id: int,
    requested_qty: int,
    reason_counter: Counter,
):
    available_qty = random.randint(0, max(requested_qty - 1, 0))
    shortage_qty = requested_qty - available_qty
    reason = weighted_shortage_reason()

    db_shortage = await ShortageService.create(
        db=db,
        product_id=product_id,
        location_id=location_id,
        requested_qty=requested_qty,
        available_qty=available_qty,
        shortage_qty=shortage_qty,
        status="unresolved",
        reason=reason,
    )

    await HistoryService.record(
        db=db,
        event_type="shortage",
        target_table="shortages",
        target_id=db_shortage.shortage_id,
        product_id=product_id,
        location_id=location_id,
        qty=requested_qty,
        status="failed",
        reason=reason,
    )

    await db.commit()

    reason_counter[reason] += 1

    return db_shortage


@router.post("/transactions")
async def seed_transactions(
    count: int = Query(10000, ge=1),
    product_count: int = Query(100, ge=1),
    location_count: int = Query(200, ge=1),
    forced_shortage_rate: float = Query(0.20, ge=0, le=1),
    db: AsyncSession = Depends(get_db),
):
    success = 0
    failed = 0

    inbound_count = 0
    outbound_count = 0
    forced_shortage_count = 0

    reason_counter = Counter()
    errors = []

    start_date = datetime(2025, 1, 2)

    for i in range(count):
        event_date = random_date(start_date, 365)

        product_id = choose_product(product_count)
        location_id = random.randint(1, location_count)

        is_outbound = random.random() < 0.65
        event_multiplier = 2 if 10 <= event_date.day <= 15 else 1

        try:
            if is_outbound:
                requested_qty = random.randint(1, 40) * event_multiplier

                if product_id <= 10:
                    requested_qty = int(requested_qty * random.uniform(1.2, 2.5))

                # 출고 중 일부는 다양한 미출 사유로 강제 생성
                if random.random() < forced_shortage_rate:
                    await create_random_shortage(
                        db=db,
                        product_id=product_id,
                        location_id=location_id,
                        requested_qty=requested_qty,
                        reason_counter=reason_counter,
                    )

                    forced_shortage_count += 1
                    success += 1
                    continue

                # 나머지 출고는 실제 재고가 있는 inventory에서 뽑기
                result = await db.execute(
                    select(Inventory).where(Inventory.stock_qty > 0)
                )
                inventories = result.scalars().all()

                if not inventories:
                    failed += 1
                    continue

                inv = random.choice(inventories)

                max_qty = min(40, inv.stock_qty)

                if max_qty <= 0:
                    failed += 1
                    continue

                outbound_qty = random.randint(1, max_qty)

                outbound_data = OutboundCreate(
                    product_id=inv.product_id,
                    location_id=inv.location_id,
                    outbound_qty=outbound_qty,
                    outbound_date=event_date,
                )

                await OutboundService.create(db, outbound_data)

                outbound_count += 1
                success += 1

            else:
                inbound_qty = random.randint(30, 180)

                inbound_data = InboundCreate(
                    product_id=product_id,
                    location_id=location_id,
                    inbound_qty=inbound_qty,
                    inbound_date=event_date,
                )

                await InboundService.create(db, inbound_data)

                inbound_count += 1
                success += 1

        except Exception as e:
            await db.rollback()
            failed += 1

            if len(errors) < 10:
                errors.append(str(e)[:200])

    return {
        "message": "입출고 거래 더미데이터 생성 완료",
        "total_requested": count,
        "success": success,
        "failed": failed,
        "inbound_count": inbound_count,
        "outbound_count": outbound_count,
        "forced_shortage_count": forced_shortage_count,
        "shortage_reasons": dict(reason_counter),
        "errors": errors,
    }


@router.get("/summary")
async def seed_summary(
    db: AsyncSession = Depends(get_db),
):
    product_count = await db.scalar(select(func.count()).select_from(Product))
    location_count = await db.scalar(select(func.count()).select_from(Location))
    inventory_count = await db.scalar(select(func.count()).select_from(Inventory))

    return {
        "products": product_count,
        "locations": location_count,
        "inventories": inventory_count,
    }