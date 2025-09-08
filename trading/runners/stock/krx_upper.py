import dataclasses
import datetime
import threading
import time

import overrides

from core.db import session
from core.finance.kis import client as kis_client
from core.utils import time as time_utils
from trading.asset import wallet as wallet_asset
from trading.database.finance import tables as data_tables
from trading.model import type as model_type
from trading.runners import base as runner_base
from trading.strategy import base as strategy_base

_TRADE_START = datetime.time(hour=14, minute=30, tzinfo=time_utils.TimeZone.SEOUL.value)


@dataclasses.dataclass
class TradeObject:
    stock_code: str


class Runner(runner_base.RealTimeTrader):
    _current_candidates: list = []
    _current_holdings: dict = {}
    _name: str = "krx_trader_upper"
    _period: int = 300  # every 5 minutes

    def __init__(
        self,
        strategy: strategy_base.UpperLimitStrategy,
        wallet: wallet_asset.KISWallet,
        max_buy_amount: int = 200_000,
        num_max_stock: int = 10,
        max_trial: int = 20,
        verbose: bool = True,
    ):
        super().__init__()
        self._strategy = strategy
        self._wallet = wallet
        self._verbose = verbose
        self._max_buy_amount = max_buy_amount
        self._num_max_stock = num_max_stock
        self._finance_database = "finance"
        self._max_trial = max_trial

    def _load_candidates(self) -> None:
        with session.get_database_session(self._finance_database) as db_session:
            corp_candidates = (
                db_session.query(data_tables.CorporateQuote)
                .filter(data_tables.CorporateQuote.rate >= 29.95)  # 상한가
                .filter(data_tables.CorporateQuote.risk == "none")
                .filter(data_tables.CorporateQuote.halt == False)  # noqa: E712
                .all()
            )

            if not corp_candidates:
                self._logger.info("There's nothing worthy to trade")
                return

            self._current_candidates = [TradeObject(c.symbol) for c in corp_candidates]

    def _update_holdings(self) -> None:
        current_holdings = self._current_holdings
        updated_holdings = self._wallet.holding_stocks

        for c in current_holdings:
            for u in updated_holdings:
                if c not in updated_holdings:
                    self._logger.info(f"stock {c} sold")
                if u not in current_holdings:
                    self._logger.info(f"stock {u} bought")

        self._current_holdings = updated_holdings

    @overrides.override
    def _on_startup(self) -> None:
        self._reset_daily_logger()
        self._current_holdings = self._wallet.holding_stocks
        self._load_candidates()

        self._logger.debug(f"Current holdings: {self._current_holdings.keys()}")
        self._logger.debug(f"Current candidates: {self._current_candidates}")

    @overrides.override
    def _on_shutdown(self) -> None:
        self._logger.debug(f"Trader {self._name} shutdown")

    @overrides.override
    def _on_buy_start(self, symbol: str) -> None:
        self._logger.debug(f"Try buying symbol {symbol}")

    @overrides.override
    def _make_buy_order(self, symbol: str, buy_price: float, quantity: int) -> None:
        stock = kis_client.get_stock(symbol)

        if not stock or self._wallet.deposit(model_type.Currency.KRW).amount < buy_price * quantity:
            self._logger.debug(f"Not enough money for stock {symbol}")
            return

        self._logger.debug(f"Placing order for symbol: {stock} at price: {buy_price} with quantity: {quantity}")
        kis_client.buy(stock=stock, qty=quantity, price=buy_price)

    @overrides.override
    def _on_sell_start(self, symbol: str) -> None:
        self._logger.debug(f"Try selling symbol {symbol}")

    @overrides.override
    def _make_sell_order(self, symbol: str, sell_price: float) -> None:
        """make sell order"""
        stock = self._current_holdings[symbol]
        stock.sell(qty=stock.qty, price=sell_price)

    @overrides.override
    def monitor_loop(self, stop_event: threading.Event):
        while not time_utils.now().time() >= _TRADE_START:
            time.sleep(self._period)

        self._logger.info(f"Trading started at {time_utils.now()}")

        for i in range(self._max_trial):
            for c in self._current_candidates:
                if c.stock_code in self._current_holdings:
                    continue

                now = time_utils.now()

                quote = kis_client.get_quote(c.stock_code)
                chart = kis_client.get_chart(
                    c.stock_code,
                    start=time_utils.get_days_before(time_utils.start_of_the_day(now), 4),
                    end=now,
                )
                if not quote or not chart:
                    continue

                prev_chart = chart.bars[-2]  # day that hit upper limit
                today_chart = chart.bars[-1]  # today

                if self._strategy.is_buyable(quote.price, prev_chart, today_chart):
                    target_price = self._strategy.target_price(today_chart)
                    quantity = max(1, self._max_buy_amount // target_price)

                    if quote.price <= target_price:
                        self._buy(c.stock_code, buy_price=quote.price, quantity=quantity)

            self._update_holdings()
            time.sleep(self._period)


_RUNNER: Runner | None = None


def run_krx_trader() -> None:
    global _RUNNER
    _RUNNER = Runner(strategy=strategy_base.UpperLimitStrategy(), wallet=wallet_asset.get_kis_wallet())
    _RUNNER.start()


def stop_krx_trader() -> None:
    global _RUNNER
    assert _RUNNER is not None, "runner is none"
    _RUNNER.end()
    _RUNNER = None


if __name__ == "__main__":
    run_krx_trader()
    stop_krx_trader()
