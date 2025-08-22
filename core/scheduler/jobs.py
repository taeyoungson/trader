from __future__ import annotations

import enum
from typing import Any, Callable, Self


class TriggerType(enum.StrEnum):
    CRON = "cron"
    DATE = "date"
    INTERVAL = "interval"


class TriggerMixin:
    _trigger: TriggerType
    _trigger_kwargs: dict

    def add_trigger(self, trigger: TriggerType, **kwargs) -> Self:
        self._trigger = trigger
        self._trigger_kwargs = kwargs

        return self

    @property
    def trigger(self) -> str:
        assert self._trigger, "Trigger Type is not set"
        return self._trigger.value

    @property
    def trigger_kwargs(self) -> dict:
        return self._trigger_kwargs


class BaseJob:
    def __init__(self, func: str | Callable, *args, **kwargs):
        self.func = func
        self._args = args
        self._kwargs = kwargs

    @property
    def id(self) -> str:
        if isinstance(self.func, str):
            return self.func
        else:
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


class APSchedulerJob(BaseJob, TriggerMixin):
    def job_arguments(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "func": self.func,
            "args": self.args,
            "kwargs": self.kwargs,
            "trigger": self.trigger,
            **self.trigger_kwargs,
        }


class TradeJob(APSchedulerJob):
    """Job class for trade"""


class RunnerJob(APSchedulerJob):
    """Job class for runner"""
