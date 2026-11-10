from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import products, orders, pages

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(products.router)
app.include_router(orders.router)
app.include_router(pages.router)
