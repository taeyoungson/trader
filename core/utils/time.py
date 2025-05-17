import datetime
import enum
import zoneinfo

from dateutil import relativedelta


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


def get_months_before(datetime_: datetime.datetime, months: int) -> datetime.datetime:
    return datetime_ - relativedelta.relativedelta(months=months)


def get_months_after(datetime_: datetime.datetime, months: int) -> datetime.datetime:
    return datetime_ + relativedelta.relativedelta(months=months)
