from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import String, TIMESTAMP, func
from typing import Optional


class Product(Base):
    __tablename__="products"
    product_id:Mapped[int]=mapped_column(primary_key=True, index=True)
    product_name:Mapped[str]=mapped_column(String(50), nullable=False)
    category:Mapped[str]=mapped_column(String(40), nullable=False)
    price:Mapped[int]=mapped_column(nullable=False)
   