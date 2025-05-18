import abc

import pydantic

from core.db import session
from core.discord import utils as discord_utils
from core.finance.kis import trader
from core.utils import time as time_utils
from trading.database.trade import tables as advisor_tables

_TRADER = None


class StockCandidate(pydantic.BaseModel):
    stock_code: str
    buy_price: float
    target_price: float
    stop_price: float


class AutoTraderBase(abc.ABC):
    _trade_database: str = "trade"
    _candidates: list[StockCandidate] = []
    _stocks: list
    _trader = trader.get_trader(use_virtual_trade=False)

    _target_profit: int

    def __init__(self, interval: int = 10):
        self.interval = interval
        self._running = False
        self._thread = None

    def _update_to_discord(self) -> None:
        message_parts = []
        current_time_str = time_utils.now().strftime("%Y-%m-%d %H:%M:%S")
        message_parts.append(f"📢 **AutoTrader Status Update at {current_time_str}** 📢")

        if self._candidates:
            message_parts.append("\n--- 🎯 **Candidate Stocks** ---")
            for i, candidate in enumerate(self._candidates):
                message_parts.append(
                    f"{i + 1}. **{candidate.stock_code}**: Buy at {candidate.buy_price:,.0f}, Target: {candidate.target_price:,.0f}, Stop: {candidate.stop_price:,.0f}"
                )
        else:
            message_parts.append("\n--- 🎯 **Candidate Stocks** ---\nNo new candidates for today.")

        if self._stocks:
            message_parts.append("\n--- 💼 **Currently Trading Stocks** ---")
            total_value = 0
            for i, stock in enumerate(self._stocks):
                current_value = stock.price * stock.quantity
                total_value += current_value
                message_parts.append(
                    f"{i + 1}. **{stock.symbol} ({stock.name})**: Qty: {stock.quantity}, Price: {stock.price:,.0f}, Value: {current_value:,.0f} {stock.currency}"
                )
            message_parts.append(
                f"Portfolio Total Value (Stocks): {total_value:,.0f} KRW (approx, based on available currency)"
            )  # Assuming KRW for total
        else:
            message_parts.append(
                "\n--- 💼 **Currently Trading Stocks** ---\nNo stocks currently held in the portfolio."
            )

        full_message = "\n".join(message_parts)
        discord_utils.send(full_message)

    def _set_buy_order(self) -> None:
        with session.get_database_session(self._trade_database) as db_session:
            candidates = (
                db_session.query(advisor_tables.StockCandidate)
                .filter(advisor_tables.StockCandidate.date == time_utils.now().strftime("%Y-%m-%d"))
                .filter(advisor_tables.StockCandidate.stock_code.not_in([s.symbol for s in self._stocks]))
                .all()
            )
            for c in candidates[:5]:
                stock = self._trader.stock(c.stock_code)

                # currenlty, just buy 1 qty
                stock.buy(qty=1, price=c.buy_price)
                self._candidates.append(
                    StockCandidate(
                        stock_code=c.stock_code,
                        buy_price=c.buy_price,
                        target_price=c.target_price,
                        stop_price=c.stop_price,
                    )
                )

    def _set_sell_order(self) -> None:
        balance = self._trader.account.balance()
        self._stocks = balance.stocks

        for s in self._stocks:
            stock = self._trader.stock(s.symbol)
            stock.sell(qty=s.quantity, price=s.price * ((100 + self._target_profit) / 100))

    def register_orders(self) -> None:
        self._set_sell_order()
        self._set_buy_order()
        self._update_to_discord()

    def cancel_orders(self) -> None:
        for order in self._trader.account.pending_orders():
            order.cancel()
