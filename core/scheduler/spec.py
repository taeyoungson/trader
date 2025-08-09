from apscheduler.jobstores import memory
from apscheduler.jobstores import sqlalchemy

from core.db import config as mysql_config
from core.db import session as mysql_session

_SCHEDULER_DB = "apscheduler"

JOBSTORES = {
    "mysql": memory.MemoryJobStore(),
    "default": sqlalchemy.SQLAlchemyJobStore(
        url=mysql_config.load_config().dsn,
        engine=mysql_session.get_or_create_engine(_SCHEDULER_DB),
    ),
}

EXECUTORS = {
    "default": {"type": "threadpool", "max_workers": 1},
}  # 1 worker due to rate limit

SCHEDULER_ARGS = {
    "coalesce": True,
    "misfire_grace_time": 360 * 60,  # 6 hour
    "max_instances": 1,
}


def get_jobstores():
    return JOBSTORES


def get_executor():
    return EXECUTORS


def get_scheduler_args():
    return SCHEDULER_ARGS
