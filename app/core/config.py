from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = "Благотворительный фонд поддержки котиков QRKot"
    app_description: str = "Сервис для поддержки котиков"
    database_url: str = "sqlite+aiosqlite:///./fastapi.db"
    secret: str = "SECRET"
    auth_secret: str = "supersecretkey123!@#"
    auth_token_lifetime_seconds: int = 3600

    class Config:
        env_file = ".env"


settings = Settings()
