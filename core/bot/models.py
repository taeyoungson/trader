import enum


class LLM(enum.StrEnum):
    GPT_4O_MINI = "gpt-4o-mini"


class Provider(enum.StrEnum):
    OPENAI = "openai"
