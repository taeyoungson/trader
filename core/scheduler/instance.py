import zoneinfo

from apscheduler.schedulers import background

from core.scheduler import spec

DefaultBackgroundScheduler = background.BackgroundScheduler(
    job_defaults=spec.get_scheduler_args(),
    jobstores=spec.get_jobstores(),
    executors=spec.get_executor(),
    timezone=zoneinfo.ZoneInfo("Asia/Seoul"),
)
