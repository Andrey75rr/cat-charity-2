from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):
    """CRUD для операций с проектами"""

    async def get_by_name(
        self,
        name: str,
        session: AsyncSession,
    ):
        """Получить проект по имени"""
        result = await session.execute(
            select(CharityProject).where(CharityProject.name == name)
        )
        return result.scalar_one_or_none()

    async def get_open_projects(
        self,
        session: AsyncSession,
    ):
        """Получить открытые проекты (не полностью инвестированные)"""
        result = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested.is_(False)
            ).order_by(CharityProject.create_date)
        )
        return result.scalars().all()


charity_project_crud = CRUDCharityProject(CharityProject)
