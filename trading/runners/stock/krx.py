import dataclasses
import threading
import time

import overrides

from core.db import session
from core.finance.kis import client as kis_client
from core.utils import time as time_utils
from trading.asset import wallet as wallet_asset
from trading.database.trade import tables as trade_tables
from trading.runners import base as runner_base
from trading.strategy import base as strategy_base


@dataclasses.dataclass
class Candidate:
    stock_code: str
    buy_at: float
    sell_at: float
    stop_at: float


class Strategy(strategy_base.StrategyBase):
    def is_buyable(self, wallet: wallet_asset, price: float) -> bool:
        return True

    def is_sellable(self, wallet: wallet_asset, price: float) -> bool:
        return True


class Runner(runner_base.AutoTraderBase):
    _name: str = "krx_trader"

    def __init__(
        self,
        strategy: strategy_base.StrategyBase,
        wallet: wallet_asset.KISWallet,
        take_profit_at: float = 0.05,
        stop_loss_at: float = 0.03,
        verbose: bool = True,
        num_candidates: int = 10,
        period: int = 60,
        max_buy_amount: int = 100_000,
        num_max_stock: int = 10,
    ):
        super().__init__()
        self._strategy = strategy
        self._take_profit_at = take_profit_at
        self._stop_loss_at = stop_loss_at
        self._wallet = wallet
        self._verbose = verbose
        self._num_candidates = num_candidates
        self._period = period
        self._max_buy_amount = max_buy_amount
        self._num_max_stock = num_max_stock

        self._current_holdings = {}
        self._current_candidates: list[Candidate] = []

    def _load_candidates(self) -> list:
        self._current_candidates = []
        with session.get_database_session(self._trade_database) as db_session:
            candidates = (
                db_session.query(trade_tables.StockCandidate)
                .filter(trade_tables.StockCandidate.date == time_utils.now().strftime("%Y-%m-%d"))
                .filter(trade_tables.StockCandidate.stock_code.not_in(self._current_holdings))
                .all()
            )
            for c in candidates[: self._num_candidates]:
                self._current_candidates.append(
                    Candidate(
                        stock_code=c.stock_code,
                        buy_at=c.buy_price,
                        sell_at=c.target_price,
                        stop_at=c.stop_price,
                    )
                )

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
        if self._strategy.is_buyable(self._wallet, buy_price * quantity):
            stock.buy(qty=quantity, price=buy_price)
        else:
            self._logger.debug(f"Not buying stock {symbol}")

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
        while not stop_event.is_set():
            self._logger.debug("Inside Monitor Loop...")
            self._update_holdings()

            # check if any stock in candidate worth buying
            if len(self._current_holdings) < self._num_max_stock:
                for c in self._current_candidates:
                    quote = kis_client.get_quote(c.stock_code)
                    if quote.price <= c.buy_at:
                        quantity = max(1, self._max_buy_amount // quote.price)
                        self._buy(c.stock_code, buy_price=c.buy_at, quantity=quantity)
                        self._current_candidates.remove(c)

            time.sleep(self._period)
