# Bean Shop

A small coffee-bean shop built to learn backend development with FastAPI, SQLAlchemy and Alembic. Visitors browse beans, add them to a cart and place an order with a shipping address (guest checkout, no accounts, no payments).

## Stack

FastAPI, SQLAlchemy 2.0, Alembic, SQLite, Jinja2 templates, vanilla JavaScript. Managed with [uv](https://docs.astral.sh/uv/).

## Run it

```bash
uv sync
uv run alembic upgrade head     # create the tables
uv run python seed.py           # add sample beans (safe to re-run)
uv run uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000> for the shop, or <http://127.0.0.1:8000/docs> for the interactive API docs. Run all commands from the project root.

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/products` | List active products |
| POST | `/api/orders` | Place an order (`201`; `404` unknown product, `409` not enough stock, `422` bad input) |
| GET | `/api/orders/{id}` | Fetch one order |

Pages: `/` (products), `/cart` (cart and checkout), `/order/{id}` (confirmation).

## How ordering works

The client sends only product ids and quantities. The server looks up prices, reserves stock with an atomic `UPDATE ... WHERE stock >= qty`, saves the order and its items in one transaction, and copies each price onto the order item so later price changes don't alter past orders. Money is stored as integer cents.

## Layout

```text
app/
  main.py        app setup, routers, static files
  database.py    engine, session, get_db
  models.py      Product, Order, OrderItem
  schemas.py     Pydantic request/response shapes
  routers/       products.py, orders.py, pages.py
  templates/     Jinja pages
  static/        app.js (cart), style.css
alembic/         migrations
seed.py          sample products
docs/            design spec
```

## Tests

```bash
uv run pytest -v
```
