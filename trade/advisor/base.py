import abc


class BaseTrader(abc.ABC):
    @abc.abstractmethod
    def screen(self) -> list[str]:
        pass

    @abc.abstractmethod
    def analyze(self):
        pass
