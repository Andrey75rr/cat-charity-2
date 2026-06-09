import asyncio
from passlib.context import CryptContext
from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_superuser():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == "root@admin.ru")
        )
        user = result.scalar_one_or_none()

        if user:
            print("Суперпользователь уже существует")
            return

        superuser = User(
            email="root@admin.ru",
            hashed_password=pwd_context.hash("root"),
            is_active=True,
            is_superuser=True,
            is_verified=True
        )
        session.add(superuser)
        await session.commit()
        print("Суперпользователь root@admin.ru создан")


if __name__ == "__main__":
    asyncio.run(create_superuser())