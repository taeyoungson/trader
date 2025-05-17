import enum


class LLM(enum.StrEnum):
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"


class Provider(enum.StrEnum):
    OPENAI = "openai"
