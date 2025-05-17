from __future__ import annotations

import enum
from typing import Callable


class TriggerType(enum.StrEnum):
    CRON = "cron"
    DATE = "date"
    INTERVAL = "interval"


class TriggerMixin:
    def __init__(self):
        self._trigger = None
        self._ctx_kwargs = None

    def add_ctx(self, trigger: TriggerType, **kwargs) -> TriggerMixin:
        self._trigger = trigger
        self._ctx_kwargs = kwargs

        return self

    @property
    def trigger(self) -> str:
        assert self._trigger, "Trigger Type is not set"
        return self._trigger.value


class BaseJob:
    def __init__(self, func: Callable, *args, **kwargs):
        self.func = func
        self._args = args
        self._kwargs = kwargs

    @property
    def id(self) -> str:
        return f"{self.func.__module__}.{self.func.__name__}.{self._kwargs.values()}"

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs

    @property
    def name(self) -> str:
        return self.id


class DefaultJob(BaseJob, TriggerMixin):
    @property
    def ctx_kwargs(self) -> dict:
        return self._ctx_kwargs
