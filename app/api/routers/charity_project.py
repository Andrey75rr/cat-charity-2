from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_name_duplicate,
    check_project_exists,
    check_project_not_closed,
    check_project_not_invested,
    check_full_amount_not_less_than_invested,
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud import charity_project_crud
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)
from app.services.investment import process_investments

router = APIRouter(prefix="/charity_project", tags=["charity_projects"])


@router.get("/", response_model=list[CharityProjectDB])
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session),
):
    return await charity_project_crud.get_all(session)


@router.post("/", response_model=CharityProjectDB)
async def create_charity_project(
    project_data: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_superuser),
):
    await check_name_duplicate(project_data.name, session)
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
    project = await check_project_exists(project_id, session)
    check_project_not_closed(project)

    update_data = project_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        await check_name_duplicate(
            update_data["name"], session, exclude_id=project_id
        )

    if "full_amount" in update_data:
        check_full_amount_not_less_than_invested(
            project, update_data["full_amount"]
        )

    return await charity_project_crud.update_project(
        project,
        update_data,
        session
    )


@router.delete("/{project_id}", response_model=CharityProjectDB)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_superuser),
):
    project = await check_project_exists(project_id, session)
    check_project_not_invested(project)
    return await charity_project_crud.remove(project, session)