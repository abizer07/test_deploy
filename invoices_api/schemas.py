# app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class InvoiceItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)


class InvoiceCreate(BaseModel):
    invoice_number: str
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None

    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None

    items: List[InvoiceItemCreate]

    tax_percentage: Optional[float] = 0
    discount: Optional[float] = 0

    currency: Optional[str] = "INR"
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class InvoiceUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    items: Optional[List[InvoiceItemCreate]] = None
    tax_percentage: Optional[float] = None
    discount: Optional[float] = None
    currency: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None
