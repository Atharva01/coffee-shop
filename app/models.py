from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from uuid import uuid4
from datetime import datetime, timezone

class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100),unique=True)
    description: Mapped[str] = mapped_column(String(200))
    weight_grams: Mapped[int] = mapped_column(Integer)
    price_cents: Mapped[int] = mapped_column(Integer)
    stock: Mapped[int] = mapped_column(Integer,default=0)
    is_active: Mapped[bool] = mapped_column(Boolean,default=True)

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[str] = mapped_column(primary_key=True,default=lambda: str(uuid4()))
    customer_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(100))
    address_line: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(100))
    postal_code: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100))
    total_cents: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    status: Mapped[str] = mapped_column(default='placed')
    items: Mapped[list["OrderItem"]] = relationship()
    

class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price_cents: Mapped[int] = mapped_column(Integer)