from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.crud import donation_crud
from app.models.user import User
from app.schemas.donation import DonationCreate, DonationDB, DonationFullInfoDB
from app.services.investment import process_investments

router = APIRouter(prefix="/donation", tags=["donations"])


@router.get("/", response_model=list[DonationFullInfoDB])
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_superuser),
):
    return await donation_crud.get_all(session)


@router.post("/", response_model=DonationDB)
async def create_donation(
    donation_data: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    new_donation = await donation_crud.create_donation(
        donation_data, user.id, session
    )
    await process_investments(session)
    await session.refresh(new_donation)
    return new_donation


@router.get("/my", response_model=list[DonationDB])
async def get_user_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    return await donation_crud.get_user_donations(user.id, session)
