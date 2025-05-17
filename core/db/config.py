import pydantic_settings


class MySqlConfig(pydantic_settings.BaseSettings):
    host: str
    port: str
    user: str
    password: str

    model_config = pydantic_settings.SettingsConfigDict(env_file=[".env"], extra="allow", env_prefix="MYSQL_")

    @property
    def dsn(self) -> str:
        return f"mysql://{self.user}:{self.password}@{self.host}:{self.port}"


def load_config() -> MySqlConfig:
    return MySqlConfig()  # pylint: disable=no-value-for-parameter
