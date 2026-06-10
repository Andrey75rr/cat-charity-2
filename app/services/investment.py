from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import charity_project_crud, donation_crud


async def process_investments(session: AsyncSession):
    """Распределяет средства из открытых пожертвований в открытые проекты"""
    projects = await charity_project_crud.get_open_projects(session)
    donations = await donation_crud.get_open_donations(session)
    changed = _distribute_investments(projects, donations)
    if changed:
        await session.commit()


def _distribute_investments(projects, donations) -> bool:
    """Распределить инвестиции между проектами и пожертвованиями"""
    changed = False
    for donation in donations:
        if donation.fully_invested:
            continue
        donation_remain = donation.full_amount - donation.invested_amount
        if donation_remain <= 0:
            continue
        changed = _invest_donation_to_projects(
            donation, donation_remain, projects
        ) or changed
    return changed


def _invest_donation_to_projects(donation, donation_remain, projects) -> bool:
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


def _close_if_fully_invested(project, donation) -> None:
    """Закрыть проект или пожертвование если достигнута цель"""
    if project.invested_amount >= project.full_amount:
        project.fully_invested = True
        project.close_date = datetime.now()
    if donation.invested_amount >= donation.full_amount:
        donation.fully_invested = True
        donation.close_date = datetime.now()
