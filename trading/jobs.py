from core.scheduler import instance
from core.scheduler import jobs

BUILD_CORPORATE_INFO_JOB = jobs.TradeJob(
    func="trading.database.finance.build_corporate_info:main",
    database="finance",
).add_trigger(
    trigger=jobs.TriggerType.CRON,
    day_of_week="0",
    hour=5,
)


BUILD_CORPORATE_QUOTE_JOB = jobs.TradeJob(
    func="trading.database.finance.build_corporate_quote:main",
    database="finance",
).add_trigger(
    trigger=jobs.TriggerType.CRON,
    day_of_week="0, 2, 4",
    hour=16,
)


BUILD_CANDIDATE_STOCK_JOB = jobs.TradeJob(
    func="trading.database.trade.build_candidate_stock:main",
    read_database="finance",
    write_database="trade",
).add_trigger(
    trigger=jobs.TriggerType.CRON,
    day_of_week="0, 1, 2, 3, 4",
    hour=7,
)


KRX_PERIODIC_JOBS = [
    jobs.RunnerJob(func="trading.runners.stock.krx_periodic:run_krx_trader").add_trigger(
        trigger=jobs.TriggerType.CRON,
        day_of_week="0, 1, 2, 3, 4",
        hour=9,
        minute=1,
    ),
    jobs.RunnerJob(func="trading.runners.stock.krx_periodic:stop_krx_trader").add_trigger(
        trigger=jobs.TriggerType.CRON,
        day_of_week="0, 1, 2, 3, 4",
        hour=15,
        minute=31,
    ),
]


FINANCE_JOBS = [
    BUILD_CORPORATE_INFO_JOB,
    BUILD_CORPORATE_QUOTE_JOB,
]


TRADE_JOBS = [
    BUILD_CANDIDATE_STOCK_JOB,
]


RUNNER_JOBS = [
    *KRX_PERIODIC_JOBS,
]


JOBS = FINANCE_JOBS + TRADE_JOBS + RUNNER_JOBS


def register_jobs() -> None:
    [
        instance.DefaultBackgroundScheduler.add_job(
            **job.job_arguments(),
            replace_existing=True,
            misfire_grace_time=3600,
        )
        for job in JOBS
    ]
