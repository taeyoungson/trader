import enum


class LLM(enum.StrEnum):
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"
    GPT_5 = "gpt-5"


class Provider(enum.StrEnum):
    OPENAI = "openai"
