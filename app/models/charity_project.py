from sqlalchemy import CheckConstraint, Column, Integer, String

from app.core.base import BaseModel


class CharityProject(BaseModel):
    __tablename__ = "charityproject"

    name = Column(String(100), unique=True, nullable=False)
    description = Column(String, nullable=False)
    full_amount = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint(
            'LENGTH(name) BETWEEN 5 AND 100',
            name='check_name_length'
        ),
        CheckConstraint(
            'LENGTH(description) >= 10',
            name='check_description_length'
        ),
        CheckConstraint(
            'full_amount > 0',
            name='check_full_amount_positive'
        ),
    )
