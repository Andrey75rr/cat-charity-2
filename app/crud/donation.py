from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.donation import Donation


class CRUDDonation(CRUDBase):
    async def get_open_donations(
        self,
        session: AsyncSession,
    ):
        result = await session.execute(
            select(Donation).where(
                Donation.fully_invested.is_(False)
            ).order_by(Donation.create_date)
        )
        return result.scalars().all()

    async def get_user_donations(
        self,
        user_id: int,
        session: AsyncSession,
    ):
        result = await session.execute(
            select(Donation).where(Donation.user_id == user_id)
        )
        return result.scalars().all()

    async def create_donation(
        self,
        donation_data,
        user_id: int,
        session: AsyncSession,
    ) -> Donation:
        new_donation = Donation(
            **donation_data.model_dump(),
            user_id=user_id,
        )
        session.add(new_donation)
        await session.commit()
        await session.refresh(new_donation)
        return new_donation


donation_crud = CRUDDonation(Donation)
