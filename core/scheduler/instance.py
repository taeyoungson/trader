import zoneinfo

from apscheduler.schedulers import background
from loguru import logger

from core.scheduler import spec


def _healthcheck() -> None:
    logger.info("Hearbeat heard")


DefaultBackgroundScheduler = background.BackgroundScheduler(
    job_defaults=spec.get_scheduler_args(),
    jobstores=spec.get_jobstores(),
    executors=spec.get_executor(),
    timezone=zoneinfo.ZoneInfo("Asia/Seoul"),
)

DefaultBackgroundScheduler.add_job(_healthcheck, "interval", minutes=60)
