import abc

from pykis.api.account.balance import KisBalance

from core.finance.kis import client as kis_client
from trading.model import type as model_type


class WalletBase(abc.ABC):
    """Base class for wallet"""


class KISWallet(WalletBase):
    _account = kis_client.get_account()

    @property
    def balance(self):
        return self._account.balance()

    @property
    def pending_orders(self):
        return self._account.pending_orders()

    @property
    def stocks(self):
        return self._account.stocks()

    def bullets(self, currency: model_type.Currency) -> KisBalance:
        return self.balance.deposit(currency.value)



def load_kis_wallet() -> KISWallet:
    return KISWallet()
