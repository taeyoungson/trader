import zoneinfo

from apscheduler import events
from apscheduler.schedulers import background
from loguru import logger

from core.discord import utils as discord_utils
from core.scheduler import spec


def _crash_report(event: events.JobEvent):
    discord_utils.send(f"Job {event.job_id} crashed with exception: {event.jobstore}")


def _heartbeat() -> None:
    logger.info("Hearbeat heard")


DefaultBackgroundScheduler = background.BackgroundScheduler(
    job_defaults=spec.get_scheduler_args(),
    jobstores=spec.get_jobstores(),
    executors=spec.get_executor(),
    timezone=zoneinfo.ZoneInfo("Asia/Seoul"),
)

DefaultBackgroundScheduler.add_job(_heartbeat, "interval", minutes=30)
DefaultBackgroundScheduler.add_listener(_crash_report, events.EVENT_JOB_ERROR)
