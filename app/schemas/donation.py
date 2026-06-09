from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DonationCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    full_amount: int = Field(..., gt=0)
    comment: str = ""


class DonationDB(BaseModel):
    id: int
    full_amount: int
    comment: str
    create_date: datetime
    model_config = ConfigDict(from_attributes=True)


class DonationFullInfoDB(DonationDB):
    user_id: int
    invested_amount: int = 0
    fully_invested: bool = False
    close_date: Optional[datetime] = None
