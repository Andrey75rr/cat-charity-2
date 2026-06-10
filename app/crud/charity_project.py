from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):
    async def get_by_name(
        self,
        name: str,
        session: AsyncSession,
    ):
        result = await session.execute(
            select(CharityProject).where(CharityProject.name == name)
        )
        return result.scalar_one_or_none()

    async def get_open_projects(
        self,
        session: AsyncSession,
    ):
        result = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested.is_(False)
            ).order_by(CharityProject.create_date)
        )
        return result.scalars().all()

    async def update_project(
        self,
        project: CharityProject,
        update_data: dict,
        session: AsyncSession,
    ) -> CharityProject:
        if "full_amount" in update_data:
            project.full_amount = update_data.pop("full_amount")
            if project.invested_amount >= project.full_amount:
                project.fully_invested = True
                project.close_date = datetime.now()

        for key, value in update_data.items():
            setattr(project, key, value)

        session.add(project)
        await session.commit()
        await session.refresh(project)
        return project


charity_project_crud = CRUDCharityProject(CharityProject)
