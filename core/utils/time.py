import datetime
import enum
import functools
import time
from typing import Any, Callable
import zoneinfo

from dateutil import relativedelta
from loguru import logger


class TimeZone(enum.Enum):
    SEOUL = zoneinfo.ZoneInfo("Asia/Seoul")
    UTC = zoneinfo.ZoneInfo("UTC")


class DateTimeFormatter(enum.Enum):
    DATE = "%Y-%m-%d"
    DATETIME_FULL = "%Y-%m-%d %H:%M:%S"
    FULL = "%Y-%m-%dT%H:%M:%S+00:00"
    COMPACTDATE = "%m/%d"
    COMPACTDATE_KR = "%m월 %d일"

    def format(self, datetime_: datetime.datetime) -> str:
        return datetime_.strftime(self.value)

    def parse(self, datetime_string: str) -> datetime.datetime:
        return datetime.datetime.strptime(datetime_string, self.value)


def now() -> datetime.datetime:
    return datetime.datetime.now(TimeZone.SEOUL.value)


def yesterday() -> datetime.datetime:
    return datetime.datetime.now() - relativedelta.relativedelta(days=1)


def get_months_before(datetime_: datetime.datetime | datetime.date, months: int) -> datetime.datetime | datetime.date:
    return datetime_ - relativedelta.relativedelta(months=months)


def get_months_after(datetime_: datetime.datetime, months: int) -> datetime.datetime:
    return datetime_ + relativedelta.relativedelta(months=months)


def get_days_after(datetime_: datetime.datetime | datetime.date, days: int) -> datetime.datetime | datetime.date:
    return datetime_ + relativedelta.relativedelta(days=days)


def get_days_before(datetime_: datetime.datetime | datetime.date, days: int) -> datetime.datetime | datetime.date:
    return datetime_ - relativedelta.relativedelta(days=days)


def start_of_the_day(datetime_: datetime.datetime) -> datetime.datetime:
    return datetime_.replace(hour=0, minute=0)


def timeit(fn: Callable) -> Any:
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        end = time.perf_counter()
        logger.info(f"func {fn.__name__} elapsed {end - start:.3f} seconds")
        return result

    return wrapper
