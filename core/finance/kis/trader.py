from loguru import logger
import pandas as pd
import pykis

from core.finance.kis import config as kis_config

_pykis_clients_cache: dict[bool, pykis.PyKis] = {}


class Trader:
    _client: pykis.PyKis  # Instance-specific client, obtained from the cache
    _use_virtual_trade: bool

    def __init__(self, use_virtual_trade: bool = True):
        self._use_virtual_trade = use_virtual_trade

        if self._use_virtual_trade not in _pykis_clients_cache:
            cfg = kis_config.load_config()
            if self._use_virtual_trade:
                logger.warning("!!! Initializing VIRTUAL KIS trading client !!!")
                client_instance = pykis.PyKis(
                    id=cfg.virtual_id,
                    account=cfg.virtual_account,
                    appkey=cfg.virtual_app_key,
                    secretkey=cfg.virtual_secret_key,
                    keep_token=True,
                )
            else:
                logger.warning("!!! Initializing LIVE KIS trading client !!!")
                client_instance = pykis.PyKis(
                    id=cfg.id,
                    account=cfg.account,
                    appkey=cfg.app_key,
                    secretkey=cfg.secret_key,
                    keep_token=True,
                )
            _pykis_clients_cache[self._use_virtual_trade] = client_instance

        self._client = _pykis_clients_cache[self._use_virtual_trade]

    @property
    def account(self):
        return self._client.account()

    def stock(self, stock_code_or_symbol: str) -> pykis.KisStock:
        return self._client.stock(stock_code_or_symbol)

    def quote(self, stock_code_or_symbol: str, market: str) -> pykis.KisQuote:
        return self._client.stock(stock_code_or_symbol, market=market).quote()

    def chart_summary(self, stock_code_or_symbol: str, *args, **kwargs) -> str:
        stock_data = self._client.stock(stock_code_or_symbol)
        chart = stock_data.chart(*args, **kwargs)

        rows = []
        if chart and chart.bars:
            for b in chart.bars:
                rows.append(
                    pd.DataFrame(
                        {
                            "Time": b.time,
                            "Open": b.open,
                            "High": b.high,
                            "Low": b.low,
                            "Close": b.close,
                            "Volume": b.volume,
                            "Amount": b.amount,
                            "Change": b.change,
                        },
                        index=[0],
                    )
                )

        if not rows:
            columns = ["Time", "Open", "High", "Low", "Close", "Volume", "Amount", "Change"]
            return pd.DataFrame(columns=columns).to_csv()

        return pd.concat(rows).to_csv()


_trader_instances_cache: dict[bool, Trader] = {}


def get_trader(use_virtual_trade: bool = True) -> Trader:
    if use_virtual_trade not in _trader_instances_cache:
        _trader_instances_cache[use_virtual_trade] = Trader(use_virtual_trade)
    return _trader_instances_cache[use_virtual_trade]
