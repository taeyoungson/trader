import threading
import time

from loguru import logger
import pydantic

from core.db import session
from core.finance.kis import trader

# from core.scheduler import instance
# from core.scheduler import jobs
from core.utils import time as time_utils
from trading.database.trade import tables as advisor_tables

_TRADER = None


class StockCandidate(pydantic.BaseModel):
    stock_code: str
    buy_price: float
    target_price: float
    stop_price: float


class GPTTrader:
    _trade_database: str = "trade"
    _trader = trader.get_trader(use_virtual_trade=False)

    def __init__(self, interval=10):
        self.interval = interval
        self._running = False
        self.thread = None
        self._candidates = []

    def pre_start(self):
        with session.get_database_session(self._trade_database) as db_session:
            candidates = (
                db_session.query(advisor_tables.StockCandidate)
                .filter(advisor_tables.StockCandidate.date == time_utils.now().strftime("%Y-%m-%d"))
                .all()
            )
            for c in candidates:
                self._candidates.append(
                    StockCandidate(
                        stock_code=c.stock_code,
                        buy_price=c.buy_price,
                        target_price=c.target_price,
                        stop_price=c.stop_price,
                    )
                )

    def start(self):
        self.pre_start()
        if not self._running:
            self._running = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()
            logger.info("Stock trader starts.")

    def _loop(self):
        while self._running:
            logger.info(f"Hi from loop!, looking for {self._candidates}")
            for c in self._candidates:
                quote = self._trader.quote(c.stock_code, market="KRX")

                if quote.price >= c.target_price:
                    logger.info(
                        f"[SIGNAL: SELL][CODE: {c.stock_code}][PRICE: {quote.price}][TARGET_PRICE: {c.target_price}]"
                    )

                elif quote.price <= c.buy_price:
                    logger.info(f"[SIGNAL: BUY][CODE: {c.stock_code}][PRICE: {quote.price}][BUY_PRICE: {c.buy_price}]")

                elif quote.price < c.stop_price:
                    logger.info(
                        f"[SIGNAL: SELL][CODE: {c.stock_code}][PRICE: {quote.price}][STOP_PRICE: {c.buy_price}]"
                    )

                else:
                    logger.info(f"[SIGNAL: IDLE][CODE: {c.stock_code}][PRICE: {quote.price}][BUY_PRICE: {c.buy_price}]")

            time.sleep(self.interval)

    def stop(self):
        self._running = False
        if self.thread:
            self.thread.join()
        logger.info("Stock monitor stopped.")


# @instance.DefaultBackgroundScheduler.scheduled_job(
#     jobs.TriggerType.CRON, id="trader_start", day_of_week="0, 1, 2, 3, 4", hour=9
# )
def start():
    global _TRADER
    assert not _TRADER
    _TRADER = GPTTrader()
    _TRADER.start()


# @instance.DefaultBackgroundScheduler.scheduled_job(
#     jobs.TriggerType.CRON, id="trader_start", day_of_week="0, 1, 2, 3, 4", hour=15, minute=30
# )
def stop():
    global _TRADER
    assert _TRADER
    _TRADER.stop()
    _TRADER = None
