import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    API_NAME: str = "Rhythmix API"
    VERSION: str = "1.0.0"
    API_STR: str = "/api/v1"


SETTINGS = Settings()
