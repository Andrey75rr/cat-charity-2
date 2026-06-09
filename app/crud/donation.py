from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.donation import Donation


class CRUDDonation(CRUDBase):
    """CRUD для операций с пожертвованиями"""

    async def get_open_donations(
        self,
        session: AsyncSession,
    ):
        """Получить открытые пожертвования (не полностью распределенные)"""
        result = await session.execute(
            select(Donation).where(
                Donation.fully_invested.is_(False)
            ).order_by(Donation.create_date)
        )
        return result.scalars().all()


donation_crud = CRUDDonation(Donation)
