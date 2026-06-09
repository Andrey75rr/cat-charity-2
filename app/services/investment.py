from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity_project import CharityProject
from app.models.donation import Donation


async def process_investments(session: AsyncSession):
    """Распределяет средства из открытых пожертвований в открытые проекты"""
    projects = await _get_open_projects(session)
    donations = await _get_open_donations(session)
    changed = await _distribute_investments(projects, donations)
    if changed:
        await session.commit()


async def _get_open_projects(session: AsyncSession):
    """Получить открытые проекты"""
    result = await session.execute(
        select(CharityProject).where(
            CharityProject.fully_invested.is_(False)
        ).order_by(CharityProject.create_date)
    )
    return result.scalars().all()


async def _get_open_donations(session: AsyncSession):
    """Получить открытые пожертвования"""
    result = await session.execute(
        select(Donation).where(
            Donation.fully_invested.is_(False)
        ).order_by(Donation.create_date)
    )
    return result.scalars().all()


async def _distribute_investments(projects, donations):
    """Распределить инвестиции между проектами и пожертвованиями"""
    changed = False
    for donation in donations:
        if donation.fully_invested:
            continue
        donation_remain = donation.full_amount - donation.invested_amount
        if donation_remain <= 0:
            continue
        changed = await _invest_donation_to_projects(
            donation, donation_remain, projects
        ) or changed
    return changed


async def _invest_donation_to_projects(donation, donation_remain, projects):
    """Инвестировать одно пожертвование в проекты"""
    changed = False
    for project in projects:
        if project.fully_invested:
            continue
        project_need = project.full_amount - project.invested_amount
        if project_need <= 0:
            continue
        investment = min(project_need, donation_remain)
        project.invested_amount += investment
        donation.invested_amount += investment
        changed = True
        donation_remain -= investment
        _close_if_fully_invested(project, donation)
        if donation.fully_invested:
            break
    return changed


def _close_if_fully_invested(project, donation):
    """Закрыть проект или пожертвование если достигнута цель"""
    if project.invested_amount >= project.full_amount:
        project.fully_invested = True
        project.close_date = datetime.now()
    if donation.invested_amount >= donation.full_amount:
        donation.fully_invested = True
        donation.close_date = datetime.now()
