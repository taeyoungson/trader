from core.scheduler import instance
from core.scheduler import jobs
from trading.auto import base

_TRADER = None


class GPTTrader(base.AutoTraderBase):
    def __init__(self, target_profit: int = 5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._target_profit = target_profit


@instance.DefaultBackgroundScheduler.scheduled_job(
    jobs.TriggerType.CRON, id="register_daily_register_job", day_of_week="0, 1, 2, 3, 4", hour=9
)
def register_daily_trade_job():
    global _TRADER
    if _TRADER is None:
        _TRADER = GPTTrader()
    _TRADER.register_orders()


@instance.DefaultBackgroundScheduler.scheduled_job(
    jobs.TriggerType.CRON, id="register_daily_cancel_order", day_of_week="0, 1, 2, 3, 4", hour=16
)
def cancel_all_orders():
    global _TRADER
    if _TRADER is not None:
        _TRADER.cancel_orders()
        _TRADER = None
