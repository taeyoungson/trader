import pydantic_settings


class Config(pydantic_settings.BaseSettings):
    crtfc_key: str

    model_config = pydantic_settings.SettingsConfigDict(env_file=".env", env_prefix="DART_", extra="allow")


def load_config() -> Config:
    return Config()
