from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.models.donation import Donation
from app.models.user import User
from app.schemas.donation import (
    DonationCreate,
    DonationDB,
    DonationFullInfoDB
)
from app.services.investment import process_investments

router = APIRouter(prefix="/donation", tags=["donations"])


@router.get("/", response_model=list[DonationFullInfoDB])
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_superuser),
):
    """Получить список всех пожертвований (только для суперпользователей)"""
    result = await session.execute(select(Donation))
    return result.scalars().all()


@router.post("/", response_model=DonationDB)
async def create_donation(
    donation_data: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Создать новое пожертвование (только для авторизованных)"""
    new_donation = Donation(
        **donation_data.model_dump(),
        user_id=user.id
    )
    session.add(new_donation)
    await session.commit()
    await session.refresh(new_donation)
    await process_investments(session)
    await session.refresh(new_donation)

    return new_donation


@router.get("/my", response_model=list[DonationDB])
async def get_user_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Получить свои пожертвования (только для авторизованных)"""
    result = await session.execute(
        select(Donation).where(Donation.user_id == user.id)
    )
    return result.scalars().all()