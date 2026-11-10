from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order, Product

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", include_in_schema=False)
def index(request: Request, db: Session = Depends(get_db)):
    products = db.scalars(
        select(Product).where(Product.is_active).order_by(Product.name)
    ).all()
    return templates.TemplateResponse(request, "index.html", {"products": products})


@router.get("/cart", include_in_schema=False)
def cart(request: Request):
    return templates.TemplateResponse(request, "cart.html")


@router.get("/order/{order_id}", include_in_schema=False)
def order_confirmation(order_id: str, request: Request, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(404, "Order not found")
    return templates.TemplateResponse(request, "confirmation.html", {"order": order})
