from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Inventory(Base):
    __tablename__ = "inventories"
    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "location_id",
            name="uq_inventory_product_location",
        ),
    )

    inventory_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.product_id"), nullable=False
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.location_id"), nullable=False
    )
    stock_qty: Mapped[int] = mapped_column(nullable=False)
