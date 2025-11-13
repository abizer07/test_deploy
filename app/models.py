from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class Transaction(BaseModel):
    date: Optional[date]
    description: Optional[str]
    debit: Optional[float]
    credit: Optional[float]
    balance: Optional[float]


class UploadResponse(BaseModel):
    filename: str
    transactions: List[Transaction]
    message: Optional[str]