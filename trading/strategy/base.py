import abc

from trading.asset import wallet as wallet_asset


class StrategyBase(abc.ABC):
    @abc.abstractmethod
    def is_buyable(self, wallet: wallet_asset.WalletBase, price: float) -> bool:
        """returns if its buy-able"""

    @abc.abstractmethod
    def is_sellable(self, wallet: wallet_asset.WalletBase, price: float) -> bool:
        """returns if its sell-able"""
