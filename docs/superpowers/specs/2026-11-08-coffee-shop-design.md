# Coffee Bean Shop: Design Spec

## Goal
A learning project. A guest visitor browses coffee beans, adds them to a cart, and places an order with a shipping address. The owner builds it by hand to learn FastAPI, SQLAlchemy and Alembic; deliverable of this effort is a phase-by-phase tutorial plan, not the code.

## Scope
**In:** product list, cart (browser), guest checkout, order confirmation page.
**Out:** payments, user accounts/auth, admin UI, shipping fees, taxes, emails, order-status API. Products are seeded by script; status is changed by hand in the DB.

## Stack
FastAPI, SQLAlchemy, Alembic, SQLite (Postgres later, optional), Jinja2 templates + small vanilla JS, pytest + httpx.

## Architecture
```
Browser (Jinja page + app.js) -> FastAPI routers -> Pydantic schemas -> SQLAlchemy session (Depends(get_db)) -> SQLite
```

```
coffee_shop/
  app/
    main.py          # create app, mount static, include routers
    database.py      # engine, SessionLocal, Base, get_db()
    models.py        # SQLAlchemy tables
    schemas.py       # Pydantic request/response shapes
    routers/
      products.py    # GET /api/products
      orders.py      # POST /api/orders, GET /api/orders/{id}
      pages.py       # HTML: /, /cart, /order/{id}
    templates/       # base.html, index.html, cart.html, confirmation.html
    static/          # app.js, style.css
  alembic/ + alembic.ini
  seed.py            # idempotent: skips existing products
  tests/test_orders.py
  requirements.txt   # fastapi, uvicorn[standard], sqlalchemy, alembic, jinja2, email-validator, pytest, httpx
```
Models describe tables; Alembic migrations create them; seed.py fills the catalog.

## Data model
| Table | Columns |
|---|---|
| products | id, name, description, price_cents, weight_grams, stock, is_active |
| orders | id (UUID string), created_at, status (placed/shipped/cancelled), customer_name, email, phone, address_line, city, postal_code, country, total_cents |
| order_items | id, order_id -> orders, product_id -> products, quantity, unit_price_cents (price snapshot) |

- Money is integer cents (floats are inexact).
- unit_price_cents is copied at order time so later price changes don't alter history.
- Order id is a random UUID so order pages can't be enumerated (no login to protect them).
- Shipping details live on the order; no customer table.

## API
| Endpoint | Purpose |
|---|---|
| GET /api/products | list active products |
| POST /api/orders | place order, 201 |
| GET /api/orders/{id} | order for confirmation page |

POST body: `{customer: {name, email, phone, address_line, city, postal_code, country}, items: [{product_id, quantity}]}`. Client never sends prices.

### Order placement (POST /api/orders)
1. Pydantic validates: items non-empty, quantity >= 1 (capped), valid email, required strings non-empty -> 422.
2. Merge duplicate product_ids by summing quantity.
3. Load products in one query (active only); unknown/inactive -> 404.
4. Reserve stock atomically per item: `UPDATE products SET stock = stock - :q WHERE id = :id AND stock >= :q`; rowcount 0 -> 409, roll back.
5. Insert Order + OrderItems, snapshot prices, compute total_cents from DB prices.
6. Single commit; any error rolls back everything (transaction).

## UI flow
- `/` Jinja product list with "Add to cart".
- `app.js` stores cart in localStorage (display only, never trusted).
- `/cart` shows cart + checkout form; submit -> fetch POST /api/orders.
- 201: clear cart, redirect to `/order/{id}`. 404/409: show message on page.

## Testing
One file, `tests/test_orders.py`, TestClient + in-memory SQLite: successful order; out of stock -> 409; unknown product -> 404; total comes from DB even if client sends a fake price.

## Build order (tutorial phases)
1. HTTP + FastAPI basics (hello world, /docs, Pydantic)
2. database.py + models.py (tables as Python classes)
3. Alembic migration (create/apply/rollback) + seed.py
4. GET /api/products (Depends(get_db))
5. POST /api/orders (validation, transaction, atomic stock, price snapshot)
6. Split into routers/schemas/models structure
7. Jinja pages + cart JS + checkout
8. pytest tests + error handling polish
Bonus: Postgres, shipping fee, order status endpoint, auth.
