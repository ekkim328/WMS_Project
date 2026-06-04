from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, TIMESTAMP, func
from typing import Optional
from datetime import datetime


class History(Base):
    __tablename__ = "histories"

    history_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # inbound, outbound, adjustment, damaged, missing, warning

    target_table: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # inbounds, outbounds, inventory 등

    target_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    # 원본 테이블의 id

    product_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    location_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(nullable=True)

    qty: Mapped[Optional[int]] = mapped_column(nullable=True)

    before_qty: Mapped[Optional[int]] = mapped_column(nullable=True)
    after_qty: Mapped[Optional[int]] = mapped_column(nullable=True)

    status: Mapped[str] = mapped_column(String(30), nullable=False, default="success")
    # success, warning, failed, missing, damaged, delayed

    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False
    )