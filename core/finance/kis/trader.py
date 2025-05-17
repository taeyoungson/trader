import pandas as pd
import pykis

from core.finance.kis import client as kis_client


class Trader:
    def __init__(self, use_virtual_trade: bool = True):
        self._use_virtual_trade = use_virtual_trade

        self._client = kis_client.get_client(self._use_virtual_trade)

    def quote(self, stock_code_or_symbol: str, market: str) -> pykis.KisQuote:
        return self._client.stock(stock_code_or_symbol, market=market).quote()

    def chart_summary(self, stock_code_or_symbol: str, *args, **kwargs) -> str:
        stock_data = self._client.stock(stock_code_or_symbol)
        chart = stock_data.chart(*args, **kwargs)

        rows = []
        for b in chart.bars:
            rows.append(
                pd.DataFrame(
                    {
                        "Time": b.time,
                        "Open": b.open,
                        "High": b.high,
                        "Low": b.low,
                        "Close": b.close,
                        "Volumn": b.volume,
                        "Amount": b.amount,
                        "Change": b.change,
                    },
                    index=[0],
                )
            )
        return pd.concat(rows).to_csv()


def get_trader(use_virtual_trade: bool = True) -> Trader:
    return Trader(use_virtual_trade)
