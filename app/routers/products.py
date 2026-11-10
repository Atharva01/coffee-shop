from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product
from app.schemas import ProductOut

router = APIRouter(prefix="/api",tags=["products"])

@router.get("/products",response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    products = db.scalars(select(Product).where(Product.is_active)).all()
    return products