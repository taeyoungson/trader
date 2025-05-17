import pydantic_settings


class LangchainConfig(pydantic_settings.BaseSettings):
    openai_api_key: str

    model_config = pydantic_settings.SettingsConfigDict(
        env_file=[".env"],
        extra="allow",
    )


def load_config() -> LangchainConfig:
    return LangchainConfig()  # pylint: disable=no-value-for-parameter
