from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime, timezone
class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: str
    weight_grams: int 
    price_cents: int
    stock: int
    
class CustomerIn(BaseModel):
    name: str = Field(min_length=1,max_length=100)
    email: EmailStr
    phone: str = Field(min_length=1,max_length=100)
    address_line: str = Field(min_length=1,max_length=100)
    city: str = Field(min_length=1,max_length=100)
    postal_code: str = Field(min_length=1,max_length=100)
    country: str = Field(min_length=1,max_length=100)
    
class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(ge=1,le=20)
    
class OrderCreate(BaseModel):
    customer: CustomerIn
    items: list[OrderItemIn] = Field(min_length=1)
    
class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    quantity: int
    unit_price_cents: int

class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    total_cents: int
    created_at: datetime
    customer_name: str
    email: str
    phone: str
    address_line: str
    city: str
    postal_code: str
    country: str
    items: list[OrderItemOut]
