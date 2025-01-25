import pydantic
import pydantic_settings


class Config(pydantic_settings.BaseSettings):
    id: str = pydantic.Field(...)
    secret_key: str = pydantic.Field(...)
    app_key: str = pydantic.Field(...)
    account: str = pydantic.Field(...)

    virtual_id: str = pydantic.Field(...)
    virtual_secret_key: str = pydantic.Field(...)
    virtual_app_key: str = pydantic.Field(...)
    virtual_account: str = pydantic.Field(...)

    model_config = pydantic_settings.SettingsConfigDict(env_file=[".env"], env_prefix="KIS_", extra="allow")


def load_config() -> Config:
    return Config()
