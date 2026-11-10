from app.database import SessionLocal
from app.models import Product

SAMPLES = [
    {"name": "Ethiopia Yirgacheffe", "description": "Light roast. Floral, citrus and bergamot notes.", "weight_grams": 250, "price_cents": 1499, "stock": 40},
    {"name": "Colombia Huila", "description": "Medium roast. Caramel, red apple and cocoa.", "weight_grams": 250, "price_cents": 1299, "stock": 60},
    {"name": "Brazil Santos", "description": "Medium-dark roast. Nutty, chocolatey, low acidity.", "weight_grams": 500, "price_cents": 1799, "stock": 50},
    {"name": "Kenya AA", "description": "Light-medium roast. Blackcurrant, bright acidity.", "weight_grams": 250, "price_cents": 1699, "stock": 30},
    {"name": "Sumatra Mandheling", "description": "Dark roast. Earthy, full-bodied, spicy finish.", "weight_grams": 250, "price_cents": 1399, "stock": 45},
    {"name": "House Espresso Blend", "description": "Dark roast. Rich crema, dark chocolate and toasted nuts.", "weight_grams": 1000, "price_cents": 2999, "stock": 25},
]

def seed():
    with SessionLocal() as db:
        for data in SAMPLES:
            exists = db.query(Product).filter_by(name=data["name"]).first()
            if not exists:
                db.add(Product(**data))
        db.commit()

if __name__ == "__main__":
    seed()
