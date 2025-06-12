import pydantic_settings


class Config(pydantic_settings.BaseSettings):
    id: str
    account: str
    app_key: str
    secret_key: str
    use_virtual_trade: bool = False

    virtual_id: str
    virtual_account: str
    virtual_app_key: str
    virtual_secret_key: str

    model_config = pydantic_settings.SettingsConfigDict(env_file=[".env"], env_prefix="KIS_", extra="allow")


def load_config() -> Config:
    return Config()
