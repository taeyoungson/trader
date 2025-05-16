import abc

from langchain import chat_models
from langchain_core import messages
from overrides import overrides

from . import config as llm_config
from . import models as llm_models


class BaseChatClient(abc.ABC):
    _system_prompt: str
    _model_provider: str

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, prompt: str) -> str:
        self._system_prompt = prompt

    @abc.abstractmethod
    def invoke(self, message: str) -> messages.AIMessage:
        pass


class OpenAIChatClient(BaseChatClient):
    _system_prompt: str
    _model_provider: str = llm_models.Provider.OPENAI

    def __init__(self, model_name: llm_models.LLM):
        self._config = llm_config.load_config()
        self._model = chat_models.init_chat_model(
            model=f"{self._model_provider}:{model_name.value}",
            api_key=self._config.openai_api_key,
        )

    @overrides
    def invoke(self, message: str) -> messages.AIMessage:
        return self._model.invoke(
            [
                messages.SystemMessage(self._system_prompt),
                messages.HumanMessage(message),
            ],
        )
