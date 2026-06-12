import random
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
import csv

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.auth import get_current_username
from app.db.database import get_db
from app.db.scheme.products import ProductCreate
from app.db.scheme.locations import LocationCreate
from app.db.scheme.inbounds import InboundCreate
from app.db.scheme.outbounds import OutboundCreate

from app.services.shortage import ShortageService
from app.services.history import HistoryService
from app.services import ProductService, LocationService, InboundService, OutboundService

# 여기서 에러 나면 inventories -> inventorys 로 바꾸기
from app.db.models.inventories import Inventory


class SeedShortageCreate(BaseModel):
    product_id: int
    location_id: int
    requested_qty: int
    available_qty: int
    shortage_qty: int
    status: str = "unresolved"
    reason: str
    created_at: datetime | None = None


router = APIRouter(
    prefix="/admin/seed",
    tags=["Admin Seed"],
    dependencies=[Depends(get_current_username)],
)


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


# 더미 상품 CSV import
@router.post("/csv-import")
async def import_products_csv(db: AsyncSession = Depends(get_db)):
    csv_path = Path(__file__).resolve().parents[2] / "data" / "products.csv"

    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            print(row)

            product = ProductCreate(
                barcode=str(row["barcode"]),
                product_name=row["product_name"],
                category=row["category"],
                price=int(row["price"]),
            )

            await ProductService.create_product_service(db, product)

    return {"message": "csv import 완료"}


@router.post("/locations")
async def seed_locations(db: AsyncSession = Depends(get_db)):
    count = 0
    zones = ["A", "B", "C", "D"]

    for zone in zones:
        for rack in range(1, 6):
            for slot in range(1, 11):
                location = LocationCreate(
                    location_name=f"{zone}-{rack:02d}-{slot:02d}",
                    zone=zone,
                )

                await LocationService.create(db, location)
                count += 1

    await db.commit()

    return {"message": "로케이션 더미데이터 생성 완료", "count": count}


@router.post("/initial-stock")
async def seed_initial_stock(
    product_count: int = Query(100),
    location_count: int = Query(200),
    db: AsyncSession = Depends(get_db),
):
    count = 0
    failed = 0
    errors = []
    base_date = datetime(2025, 1, 1, 9, 0)

    for product_id in range(1, product_count + 1):
        selected_locations = random.sample(
            range(1, location_count + 1),
            random.randint(2, 4),
        )

        for location_id in selected_locations:
            inbound = InboundCreate(
                product_id=product_id,
                location_id=location_id,
                inbound_qty=random.randint(300, 900),
                inbound_date=base_date,
            )

            try:
                await InboundService.create(db, inbound)
                count += 1
            except Exception as e:
                await db.rollback()
                failed += 1
                if len(errors) < 10:
                    errors.append(str(e)[:200])

    return {
        "message": "초기 재고 생성 완료",
        "count": count,
        "failed": failed,
        "errors": errors,
    }


@router.post("/transactions")
async def seed_transactions(
    count: int = Query(10000),
    product_count: int = Query(100),
    location_count: int = Query(200),
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

    popular_products = list(range(1, 11))
    start_date = datetime(2025, 1, 2)

    for i in range(count):
        event_date = start_date + timedelta(days=random.randint(0, 365))
        event_date = event_date.replace(
            hour=random.randint(8, 22),
            minute=random.randint(0, 59),
        )

        product_id = (
            random.choice(popular_products)
            if random.random() < 0.45
            else random.randint(1, product_count)
        )

        location_id = random.randint(1, location_count)

        is_outbound = random.random() < 0.65
        event_multiplier = 2 if 10 <= event_date.day <= 15 else 1

        try:
            if is_outbound:
                qty = random.randint(1, 40) * event_multiplier

                if product_id in popular_products:
                    qty = int(qty * random.uniform(1.2, 2.5))

                requested_qty = max(qty, 1)

                # 여기서 다양한 미출 사유 직접 생성
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

                # 나머지 정상 출고는 실제 재고 있는 inventory에서 뽑기
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

                outbound = OutboundCreate(
                    product_id=inv.product_id,
                    location_id=inv.location_id,
                    outbound_qty=outbound_qty,
                    outbound_date=event_date,
                )

                await OutboundService.create(db, outbound)

                outbound_count += 1
                success += 1

            else:
                inbound = InboundCreate(
                    product_id=product_id,
                    location_id=location_id,
                    inbound_qty=random.randint(30, 180),
                    inbound_date=event_date,
                )

                await InboundService.create(db, inbound)

                inbound_count += 1
                success += 1

        except Exception as e:
            await db.rollback()
            failed += 1

            if len(errors) < 10:
                errors.append(str(e)[:300])

    return {
        "message": "입출고 더미데이터 생성 완료",
        "total_requested": count,
        "success": success,
        "failed": failed,
        "inbound_count": inbound_count,
        "outbound_count": outbound_count,
        "forced_shortage_count": forced_shortage_count,
        "shortage_reasons": dict(reason_counter),
        "errors": errors,
    }


# 미출데이터 단건 생성
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