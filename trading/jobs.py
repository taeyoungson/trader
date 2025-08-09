from core.scheduler import instance
from core.scheduler import jobs
from trading.database.finance import build_corporate_info
from trading.database.finance import build_corporate_quote
from trading.database.trade import build_candidate_stock
from trading.runners.stock import krx_periodic

BUILD_CORPORATE_INFO_JOB = jobs.TradeJob(
    func=build_corporate_info.main,
    database="finance",
).add_ctx(
    trigger=jobs.TriggerType.CRON,
    day_of_week="0",
    hour=5,
)


BUILD_CORPORATE_QUOTE_JOB = jobs.TradeJob(
    func=build_corporate_quote.main,
    database="finance",
).add_ctx(
    trigger=jobs.TriggerType.CRON,
    day_of_week="0, 2, 4",
    hour=16,
)


BUILD_CANDIDATE_STOCK_JOB = jobs.TradeJob(
    func=build_candidate_stock.main,
    read_database="finance",
    write_database="trade",
).add_ctx(
    trigger=jobs.TriggerType.CRON,
    day_of_week="0, 1, 2, 3, 4",
    hour=7,
)


KRX_PERIODIC_JOBS = [
    jobs.RunnerJob(
        func=krx_periodic.run_krx_trader,
    ).add_ctx(
        trigger=jobs.TriggerType.CRON,
        day_of_week="0, 1, 2, 3, 4",
        hour=9,
    ),
    jobs.RunnerJob(
        func=krx_periodic.stop_krx_trader,
    ).add_ctx(
        trigger=jobs.TriggerType.CRON,
        day_of_week="0, 1, 2, 3, 4",
        hour=15,
        minute=30,
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
            id=job.id,
            name=job.name,
            func=job.func,
            args=job.args,
            kwargs=job.kwargs,
            trigger=job.trigger,
            **job.ctx_kwargs,
        )
        for job in JOBS
    ]
