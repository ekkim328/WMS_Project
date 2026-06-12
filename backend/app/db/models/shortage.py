from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, TIMESTAMP, func
from datetime import datetime
from typing import Optional


class Shortage(Base):
    __tablename__ = "shortages"

    shortage_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    product_id: Mapped[int] = mapped_column(nullable=False)
    location_id: Mapped[int] = mapped_column(nullable=False)

    requested_qty: Mapped[int] = mapped_column(nullable=False)
    available_qty: Mapped[int] = mapped_column(nullable=False)
    shortage_qty: Mapped[int] = mapped_column(nullable=False)

    status: Mapped[str] = mapped_column(String(30), nullable=False, default="unresolved")
    # unresolved, resolved, ignored

    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False
    )