import abc

import pykis

from trading.asset import wallet as wallet_asset


class StrategyBase(abc.ABC):
    @abc.abstractmethod
    def is_buyable(self, *args, **kwargs) -> bool:
        """returns if its buy-able"""

    @abc.abstractmethod
    def is_sellable(self, *args, **kwargs) -> bool:
        """returns if its sell-able"""


class BasicStrategy(StrategyBase):
    def is_buyable(self, *args, **kwargs) -> bool:
        return True

    def is_sellable(self, *args, **kwargs) -> bool:
        return True


class UpperLimitStrategy(BasicStrategy):
    @staticmethod
    def target_price(today_chart: pykis.KisChartBar) -> int:
        low = float(today_chart.low)
        high = float(today_chart.high)

        return int((high - low) // 4 + low)

    def is_buyable(self, price: float, prev_chart: pykis.KisChartBar, today_chart: pykis.KisChartBar) -> bool:
        # make sure `yesterday` was the day that hit upper limit
        upper_limit = float((prev_chart.close - prev_chart.open) / prev_chart.open) > 0.29
        amount_condition = float(prev_chart.amount) * 1.1 <= today_chart.amount
        open_price_condition = float(prev_chart.close) * 1.01 <= today_chart.open <= float(prev_chart.close) * 1.1
        price_condition = price >= today_chart.low

        return upper_limit & amount_condition & open_price_condition & price_condition

    def is_sellable(self, wallet: wallet_asset.WalletBase, price: float) -> bool:
        """returns if its sell-able"""
