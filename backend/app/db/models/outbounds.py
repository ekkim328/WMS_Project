from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import String, TIMESTAMP, func, ForeignKey
from typing import Optional


class Outbound(Base):
    __tablename__="outbounds"
    outbound_id:Mapped[int]=mapped_column(primary_key=True, index=True)
    product_id:Mapped[int]=mapped_column(ForeignKey("locations.location_id"), nullable=False)
    location_id:Mapped[int]=mapped_column(ForeignKey("locations.location_id"), nullable=False)
    outbound_qty:Mapped[int]=mapped_column(nullable=False)
    outbound_date:Mapped[datetime]=mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)