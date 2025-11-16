"""
Database Schemas for YOTS TECH-SHOP

Each Pydantic model represents a MongoDB collection. Collection name is the
lowercase of the class name (e.g., Product -> "product").
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime


class Product(BaseModel):
    """Product catalog items (new, pre-owned, accessories)"""
    name: str = Field(..., description="Product display name")
    description: Optional[str] = Field(None, description="Long description")
    price: float = Field(..., ge=0, description="Price in USD")
    category: str = Field(..., description="new | preowned | accessories")
    is_new: bool = Field(True, description="True for brand-new items")
    condition: Optional[str] = Field(None, description="Condition label for pre-owned: Like New, Excellent, Good")
    grade: Optional[str] = Field(None, description="Grade for pre-owned items: A, B, C")
    storage: Optional[str] = Field(None, description="Storage capacity e.g. 128GB")
    color: Optional[str] = Field(None, description="Color variant")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    stock: int = Field(0, ge=0, description="Available inventory")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OrderItem(BaseModel):
    product_id: str = Field(..., description="Mongo ObjectId as string")
    name: str
    price: float
    quantity: int = Field(..., ge=1)
    image: Optional[str] = None
    storage: Optional[str] = None
    color: Optional[str] = None


class Customer(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str


class Order(BaseModel):
    """Customer order created at checkout"""
    items: List[OrderItem]
    subtotal: float = Field(..., ge=0)
    shipping: float = Field(..., ge=0)
    total: float = Field(..., ge=0)
    customer: Customer
    status: str = Field("pending", description="pending | paid | shipped | completed | cancelled")
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Optional: lightweight category descriptor for UI
class Category(BaseModel):
    key: str = Field(..., description="new | preowned | accessories")
    label: str = Field(..., description="Human-readable label")
