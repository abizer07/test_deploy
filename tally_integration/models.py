# tally_integration/models.py
# Placeholder for future DB models (SQLModel, SQLAlchemy, or ODM)
# Example Pydantic model for local logging (not persisted)
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TallyLog(BaseModel):
    voucher_type: str
    narration: str
    amount: float
    status: str
    raw_response: Optional[str] = None
    created_at: datetime = datetime.utcnow()
