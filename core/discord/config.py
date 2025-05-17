import pydantic
import pydantic_settings


class Config(pydantic_settings.BaseSettings):
    webhook: str | None = pydantic.Field(None)

    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="DISCORD_",
        env_file=[".env"],
        extra="allow",
    )


def load_config() -> Config:
    return Config()  # pylint: disable=no-value-for-parameter
