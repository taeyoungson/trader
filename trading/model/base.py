import abc

from core.db import session
from core.finance.kis import client as kis_client
from core.utils import time as time_utils
from trading.model import wallet
from trading.model import type as model_type
from trading.mixin import configs as config_mixin
from trading.database.trade import tables as trade_tables


class TraderBase(abc.ABC):
    _trade_database: str = "trade"
    _holding_stocks: list
    _candidate_stocks: list

    @abc.abstractmethod
    def _load_candidate_stock(self) -> None:
        pass

    @abc.abstractmethod
    def _on_startup(self) -> None:
        """Executed on trade starts"""

    @abc.abstractmethod
    def _on_end(self) -> None:
        """Executed on trade ends"""

    def _on_buy_start(self, symbol: str) -> None:
        """Executed after buy order"""

    def _on_buy_end(self, symbol: str) -> None:
        """Executed after buy order"""

    @abc.abstractmethod
    def _make_buy_order(self, symbol: str, **kwargs) -> None:
        """make buy order"""

    @abc.abstractmethod
    def _is_meet_buy_condition(self) -> None:
        """returns if its buy-able"""

    def buy(self, symbol: str, **kwargs) -> None:
        self._on_buy_start(symbol)
        self._make_buy_order(symbol, **kwargs)
        self._on_buy_end(symbol)

    def _on_sell_start(self, symbol: str) -> None:
        """Executed before sell order"""

    def _on_sell_end(self, symbol: str) -> None:
        """Executed after sell order"""

    @abc.abstractmethod
    def _make_sell_order(self, symbol: str) -> None:
        """make sell order"""

    def sell(self, symbol: str) -> None:
        self._on_sell_start(symbol)
        self._make_sell_order(symbol)
        self._on_sell_end(symbol)

    @abc.abstractmethod
    def monitor_loop(self):
        pass

    def start(self):
        self._on_startup()
        # do your loop here

    def end(self):
        # exit your loop here
        self._on_end()


class KISAutoTrader(
    TraderBase,
    config_mixin.TargetObjectiveMixin,
    config_mixin.BuyStrategyMixin,
):
    def __init__(self):
        self._wallet = wallet.load_kis_wallet()

        self._holding_stocks = [s.symbol for s in self._wallet.stocks]
        self._candidate_stocks = []

    def _load_candidate_stock(self):
        with session.get_database_session(self._trade_database) as db_session:
            candidates = (
                db_session.query(trade_tables.StockCandidate)
                .filter(trade_tables.StockCandidate.date == time_utils.now().strftime("%Y-%m-%d"))
                .filter(trade_tables.StockCandidate.stock_code.not_in([s.symbol for s in self._holding_stocks]))
                .all()
            )

            for c in candidates[:self._maximum_trading_number_of_stocks - len(self._holding_stocks)]:
                self._candidate_stocks.append(
                    model_type.StockCandidate(
                        stock_code=c.stock_code,
                        buy_price=c.buy_price,
                        target_price=c.target_price,
                        stop_price=c.stop_price,
                    )
                )


    def _on_startup(self) -> None:
        self._load_candidate_stock()

        for stock in self._holding_stocks:
            if stock.profit_rate >= self._target_profit_rate:
                self.sell(stock.symbol)

        for candidate in self._candidate_stocks:
            self.buy(candidate.stock_code)

    def _on_end(self) -> None:
        for order in self._wallet.pending_orders():
            order.cancel()

    def _is_meet_buy_condition(self) -> bool:
        purchase_amount = self._wallet.balance.purchase_amount
        current_amount = self._wallet.balance.current_amount

        if purchase_amount > self._ratio_remainder_to_total * (purchase_amount + current_amount):
            return False
        return True

    def _make_buy_order(self, symbol: str, **kwargs) -> None:
        if self._is_meet_buy_condition():
            kis_client.get_stock(symbol).buy(**kwargs)

    def _make_sell_order(self, symbol: str) -> None:
        stock = self._wallet.balance.stock(symbol)
        stock.sell()

    def monitor_loop(self):
        pass
