import dataclasses

import overrides

from core.db import session
from core.finance.kis import client as kis_client
from core.utils import indicator as indicator_utils
from core.utils import time as time_utils
from trading.asset import wallet as wallet_asset
from trading.database.trade import tables as trade_tables
from trading.model import type as model_type
from trading.runners import base as runner_base
from trading.strategy import base as strategy_base


@dataclasses.dataclass
class TradeObject:
    stock_code: str
    support_price: int
    resistance_price: int


class Strategy(strategy_base.StrategyBase):
    def is_buyable(self, wallet: wallet_asset.KISWallet, price: float) -> bool:
        return wallet.deposit(model_type.Currency.KRW).amount > price

    def is_sellable(self, wallet: wallet_asset.KISWallet, price: float) -> bool:
        return True


class Runner(runner_base.PeriodicTrader):
    _current_candidates: list = []
    _current_holdings: dict = {}
    _name: str = "krx_trader"

    def __init__(
        self,
        strategy: strategy_base.StrategyBase,
        wallet: wallet_asset.KISWallet,
        num_candidates: int = 10,
        period: int = 60,
        max_buy_amount: int = 100_000,
        num_max_stock: int = 10,
        verbose: bool = True,
    ):
        super().__init__()
        self._strategy = strategy
        self._wallet = wallet
        self._verbose = verbose
        self._num_candidates = num_candidates
        self._period = period
        self._max_buy_amount = max_buy_amount
        self._num_max_stock = num_max_stock

    def _load_candidates(self) -> None:
        with session.get_database_session(self._database) as db_session:
            candidates = (
                db_session.query(trade_tables.StockCandidate)
                .filter(trade_tables.StockCandidate.date == time_utils.now().strftime("%Y-%m-%d"))
                .filter(trade_tables.StockCandidate.stock_code.not_in(self._current_holdings))
                .filter(trade_tables.StockCandidate.growth_score >= 5)
                .filter(trade_tables.StockCandidate.financial_stability_score >= 5)
                .filter(trade_tables.StockCandidate.valuation_attractiveness.in_(["Undervalued", "Fairly valued"]))
                .filter(
                    trade_tables.StockCandidate.technical_signal.in_(
                        [
                            "Golden Cross Occured",
                            "Entering Oversold Territory",
                            "Range Bound Movement",
                            "Approaching Key Support",
                        ]
                    )
                )
                .all()
            )
            for c in candidates[: self._num_candidates]:
                self._current_candidates.append(
                    TradeObject(
                        stock_code=c.stock_code,
                        support_price=c.support_price,
                        resistance_price=c.resistance_price,
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
            kis_client.buy(stock=stock, qty=quantity, price=buy_price)
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
    def start(self) -> None:
        self._on_startup()
        self._update_holdings()

        num_to_buy_stock = max(self._num_max_stock - len(self._current_holdings), 0)

        for c in self._current_candidates[:num_to_buy_stock]:
            quote = kis_client.get_quote(c.stock_code)

            if not quote:
                continue

            target_prices = indicator_utils.get_finbonacci_fallback(c.support_price, c.resistance_price)

            # currently, just use 0.236
            if quote.price <= target_prices[0]:
                price = min(quote.price, target_prices[0])
                quantity = max(1, self._max_buy_amount // price)
                self._buy(c.stock_code, buy_price=price, quantity=quantity)

    @overrides.override
    def end(self) -> None:
        pass


_RUNNER: Runner | None = None


def run_krx_trader() -> None:
    global _RUNNER
    _RUNNER = Runner(strategy=Strategy(), wallet=wallet_asset.get_kis_wallet())
    _RUNNER.start()


def stop_krx_trader() -> None:
    global _RUNNER
    assert _RUNNER is not None, "runner is none"
    _RUNNER.end()
    _RUNNER = None
