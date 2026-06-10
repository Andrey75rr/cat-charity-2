from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import charity_project_crud
from app.models.charity_project import CharityProject


async def check_name_duplicate(
    name: str,
    session: AsyncSession,
    exclude_id: int | None = None,
) -> None:
    existing = await charity_project_crud.get_by_name(name, session)
    if existing and existing.id != exclude_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Проект с таким именем уже существует!",
        )


async def check_project_exists(
    project_id: int,
    session: AsyncSession,
) -> CharityProject:
    project = await charity_project_crud.get(project_id, session)
    if not project:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Проект не найден",
        )
    return project


def check_project_not_closed(project: CharityProject) -> None:
    if project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Закрытый проект нельзя редактировать!",
        )


def check_project_not_invested(project: CharityProject) -> None:
    if project.invested_amount > 0 or project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="В проект были внесены средства, не подлежит удалению!",
        )


def check_full_amount_not_less_than_invested(
    project: CharityProject,
    new_full_amount: int,
) -> None:
    if new_full_amount < project.invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Нельзя установить значение full_amount меньше "
                   "уже вложенной суммы.",
        )
