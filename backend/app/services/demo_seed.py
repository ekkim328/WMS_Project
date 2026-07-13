import csv
from datetime import datetime, timedelta
import logging
import os
from pathlib import Path
import random

from sqlalchemy import func, select

from app.db.database import AsyncSessionLocal
from app.db.models import Inbound, Inventory, Location, Outbound, Product, Shortage


logger = logging.getLogger(__name__)


def demo_seed_enabled() -> bool:
    return os.getenv("AUTO_SEED_DEMO_DATA", "").lower() in {"1", "true", "yes"}


async def _row_count(db, model) -> int:
    return int(await db.scalar(select(func.count()).select_from(model)) or 0)


async def seed_demo_data_if_empty() -> dict[str, int | bool]:
    """Populate an empty deployment database without touching existing data."""
    if not demo_seed_enabled():
        return {"enabled": False}

    async with AsyncSessionLocal() as db:
        existing_rows = sum(
            [
                await _row_count(db, Product),
                await _row_count(db, Location),
                await _row_count(db, Inventory),
                await _row_count(db, Inbound),
                await _row_count(db, Outbound),
                await _row_count(db, Shortage),
            ]
        )
        if existing_rows:
            result = {"enabled": True, "skipped": True, "existing_rows": existing_rows}
            logger.info("Demo seed skipped because warehouse data already exists: %s", result)
            return result

        products = []
        csv_path = Path(__file__).resolve().parents[2] / "data" / "products.csv"
        with csv_path.open(encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                product = Product(
                    barcode=str(row["barcode"]),
                    product_name=row["product_name"],
                    category=row["category"],
                    price=int(row["price"]),
                )
                db.add(product)
                products.append(product)

        locations = []
        for zone in ("A", "B", "C", "D"):
            for rack in range(1, 6):
                for slot in range(1, 11):
                    location = Location(
                        location_name=f"{zone}-{rack:02d}-{slot:02d}",
                        zone=zone,
                    )
                    db.add(location)
                    locations.append(location)

        await db.flush()

        rng = random.Random(20260713)
        base_date = datetime(2025, 1, 1, 9, 0)
        created_operations = 0

        for product_index, product in enumerate(products):
            selected_locations = rng.sample(locations, min(3, len(locations)))

            for location_index, location in enumerate(selected_locations):
                inbound_qty = rng.randint(300, 900)
                outbound_qty = rng.randint(20, min(150, inbound_qty - 1))
                inbound_date = base_date + timedelta(days=rng.randint(0, 120))
                outbound_date = inbound_date + timedelta(days=rng.randint(1, 120))

                db.add(
                    Inventory(
                        product_id=product.product_id,
                        location_id=location.location_id,
                        stock_qty=inbound_qty - outbound_qty,
                    )
                )
                db.add(
                    Inbound(
                        product_id=product.product_id,
                        location_id=location.location_id,
                        inbound_qty=inbound_qty,
                        inbound_date=inbound_date,
                    )
                )
                db.add(
                    Outbound(
                        product_id=product.product_id,
                        location_id=location.location_id,
                        outbound_qty=outbound_qty,
                        outbound_date=outbound_date,
                    )
                )
                created_operations += 1

                if product_index % 10 == 0 and location_index == 0:
                    db.add(
                        Shortage(
                            product_id=product.product_id,
                            location_id=location.location_id,
                            requested_qty=120,
                            available_qty=40,
                            shortage_qty=80,
                            status="unresolved",
                            reason="데모 데이터 재고 부족",
                        )
                    )

        await db.commit()

        result = {
            "enabled": True,
            "skipped": False,
            "products": len(products),
            "locations": len(locations),
            "operation_sets": created_operations,
        }
        logger.info("Demo seed completed: %s", result)
        return result
