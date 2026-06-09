from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud import charity_project_crud
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate
)
from app.services.investment import process_investments

router = APIRouter(prefix="/charity_project", tags=["charity_projects"])


@router.get("/", response_model=list[CharityProjectDB])
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session),
):
    """Получить список всех проектов"""
    return await charity_project_crud.get_all(session)


@router.post("/", response_model=CharityProjectDB)
async def create_charity_project(
    project_data: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_superuser),
):
    existing = await charity_project_crud.get_by_name(
        project_data.name, session
    )
    if existing:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Проект с таким именем уже существует!"
        )

    new_project = await charity_project_crud.create(project_data, session)

    await process_investments(session)

    await session.refresh(new_project)

    return new_project


@router.patch("/{project_id}", response_model=CharityProjectDB)
async def update_charity_project(
    project_id: int,
    project_data: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_superuser),
):
    """Редактировать проект (только для суперпользователей)"""
    project = await charity_project_crud.get(project_id, session)
    if not project:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Проект не найден"
        )

    if project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Закрытый проект нельзя редактировать!"
        )

    update_data = project_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        existing = await charity_project_crud.get_by_name(
            update_data["name"], session
        )
        if existing and existing.id != project_id:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Проект с таким именем уже существует!"
            )

    if "full_amount" in update_data:
        if update_data["full_amount"] < project.invested_amount:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Нельзя установить значение full_amount меньше "
                       "уже вложенной суммы."
            )
        project.full_amount = update_data["full_amount"]
        del update_data["full_amount"]

        if project.invested_amount >= project.full_amount:
            project.fully_invested = True
            project.close_date = datetime.now()

    for key, value in update_data.items():
        setattr(project, key, value)

    await session.commit()
    await session.refresh(project)
    return project


@router.delete("/{project_id}", response_model=CharityProjectDB)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_superuser),
):
    """Удалить проект (только для суперпользователей)"""
    project = await charity_project_crud.get(project_id, session)
    if not project:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Проект не найден"
        )

    if project.invested_amount > 0 or project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="В проект были внесены средства, не подлежит удалению!"
        )

    return await charity_project_crud.remove(project, session)
