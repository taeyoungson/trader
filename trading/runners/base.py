import abc
import os
import sys
import threading

import loguru
import overrides

from core.utils import time as time_utils


class AutoTraderBase(abc.ABC):
    _name: str
    _database: str = "trade"
    _logger = loguru.logger

    def _reset_daily_logger(self) -> None:
        self._logger.remove()

        os.makedirs(f"logs/{self._name}", exist_ok=True)

        log_file = f"logs/{self._name}/{time_utils.now().strftime('%Y-%m-%d')}.log"

        self._logger.add(log_file, level="DEBUG", rotation="00:00", retention="7 days")
        self._logger.add(sys.stderr, level="INFO")

        self._logger.info(f"#### Logging for {self._name} started ####")

    @abc.abstractmethod
    def _on_startup(self) -> None:
        """Executed on trade starts"""

    @abc.abstractmethod
    def _on_shutdown(self) -> None:
        """Executed on trade ends"""

    def _on_buy_start(self, symbol: str) -> None:
        """Executed after buy order"""

    def _on_buy_end(self, symbol: str) -> None:
        """Executed after buy order"""

    @abc.abstractmethod
    def _make_buy_order(self, symbol: str, buy_price: float, quantity: int) -> None:
        """make buy order"""

    def _buy(self, symbol: str, **kwargs) -> None:
        self._on_buy_start(symbol)
        self._make_buy_order(symbol, **kwargs)
        self._on_buy_end(symbol)

    def _on_sell_start(self, symbol: str) -> None:
        """Executed before sell order"""

    def _on_sell_end(self, symbol: str) -> None:
        """Executed after sell order"""

    @abc.abstractmethod
    def _make_sell_order(self, symbol: str, sell_price: float) -> None:
        """make sell order"""

    def _sell(self, symbol: str, sell_price: float) -> None:
        self._on_sell_start(symbol)
        self._make_sell_order(symbol, sell_price)
        self._on_sell_end(symbol)

    @abc.abstractmethod
    def start(self):
        """start function"""

    @abc.abstractmethod
    def end(self):
        """end function"""


class PeriodicTrader(AutoTraderBase, abc.ABC):
    """Make buy and sell order at pre-designated time slots"""


class RealTimeTrader(AutoTraderBase, abc.ABC):
    def __init__(self):
        self._monitor_thread = None
        self._stop_event = threading.Event()

    @abc.abstractmethod
    def monitor_loop(self, stop_event: threading.Event):
        pass

    def _run_monitor_loop(self):
        self.monitor_loop(self._stop_event)

    @overrides.override
    def start(self):
        self._on_startup()
        self._monitor_thread = threading.Thread(target=self._run_monitor_loop, daemon=True)
        self._monitor_thread.start()
        self._logger.info("✅ Monitor Thread Starts!")

    @overrides.override
    def end(self):
        self._stop_event.set()
        self._logger.info("🛑 Monitor Thread Shutdown requested")

        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join()
            self._logger.info("🧹 Monitor Thread Cleaned up")

        self._on_shutdown()
