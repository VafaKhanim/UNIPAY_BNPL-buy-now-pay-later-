from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    debug: bool = False
    min_credit_score: int = 500

    model_config = {"env_file": ".env"}


settings = Settings()