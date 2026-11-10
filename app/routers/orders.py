from sqlalchemy import select, update
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from app.models import Product, Order, OrderItem
from app.database import get_db
from app.schemas import OrderOut, OrderCreate
router = APIRouter(prefix="/api",tags=["orders"])

@router.post("/orders",response_model=OrderOut, status_code=201)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    wanted: dict[int,int] = {}
    for item in payload.items:
        wanted[item.product_id] = wanted.get(item.product_id,0) + item.quantity
    
    rows = db.scalars(
        select(Product).where(Product.id.in_(wanted), Product.is_active)
    ).all()
    by_id = {p.id: p for p in rows}
    
    missing = set(wanted) - set(by_id)
    if missing:
        raise HTTPException(404,f"Unknown product ids:{sorted(missing)}")
    
    for pid in sorted(wanted):
        qty = wanted[pid]
        result = db.execute(
            update(Product)
            .where(Product.id == pid, Product.stock >= qty)
            .values(stock=Product.stock - qty)
        )
        if result.rowcount == 0:
            db.rollback()
            raise HTTPException(409, f"Not enough stock for {by_id[pid].name}")
    
    total = sum(by_id[pid].price_cents * qty for pid, qty in wanted.items())
    
    c = payload.customer
    order = Order(
        customer_name=c.name, email=c.email, phone=c.phone,
        address_line=c.address_line, city=c.city,
        postal_code=c.postal_code, country=c.country,
        total_cents=total,
    )
    
    db.add(order)
    db.flush()
    
    db.add_all(
        [
            OrderItem(order_id=order.id,product_id=pid, quantity=qty,
                      unit_price_cents=by_id[pid].price_cents)
        
        for pid, qty in wanted.items()
        ]
    )
    db.commit()
    db.refresh(order)
    return order

@router.get("/orders/{order_id}",response_model=OrderOut,status_code=200)
def get_order(order_id: str, db:Session=Depends(get_db)):
    order = db.get(Order,order_id)
    if order is None:
        raise HTTPException(404,"Order not found")
    return order