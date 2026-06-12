from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Location(Base):
    __tablename__ = "locations"
    __table_args__ = (
        UniqueConstraint(
            "location_name",
            "zone",
            name="uq_location_name_zone",
        ),
    )
    location_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    location_name: Mapped[str] = mapped_column(String(50), nullable=False)
    zone: Mapped[str] = mapped_column(String(2), nullable=False)
