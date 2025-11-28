# app/models.py
from beanie import Document
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class InvoiceItem(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    total_price: float


class Invoice(Document):
    invoice_number: str
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None

    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None

    items: List[InvoiceItem]

    sub_total: float
    tax_percentage: Optional[float] = 0
    tax_amount: Optional[float] = 0
    discount: Optional[float] = 0
    grand_total: float

    currency: str = "INR"
    status: str = "DRAFT"  # DRAFT, PAID, CANCELLED

    issued_date: datetime = Field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None

    notes: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "invoices"   # MongoDB collection name
