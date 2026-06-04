from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import String, TIMESTAMP, func, ForeignKey
from typing import Optional


class Location(Base):
    __tablename__="locations"
    location_id:Mapped[int]=mapped_column(primary_key=True, index=True)
    location_name:Mapped[str]=mapped_column(String(50), nullable=False)
    zone:Mapped[str]=mapped_column(String(2), nullable=False)
    