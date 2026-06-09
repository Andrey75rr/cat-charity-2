from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.base import BaseModel


class Donation(BaseModel):
    __tablename__ = "donation"

    comment = Column(String, nullable=True, default="")
    full_amount = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    user = relationship("User", backref="donations")

    __table_args__ = (
        CheckConstraint('full_amount > 0', name='check_full_amount_positive'),
    )
