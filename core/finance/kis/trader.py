import pandas as pd

from core.finance.kis import client as kis_client


class Trader:
    def __init__(self, use_virtual_trade: bool = True):
        self._use_virtual_trade = use_virtual_trade

        self._client = kis_client.get_client(self._use_virtual_trade)

    def quote_summary(self, stock_code_or_symbol: str) -> str:
        quote = self._client.stock(stock_code_or_symbol).quote()
        return f"""
            종목코드: {quote.symbol}
            종목명: {quote.name}
            종목시장: {quote.market}

            업종명: {quote.sector_name}

            현재가: {quote.price}
            거래량: {quote.volume}
            거래대금: {quote.amount}
            시가총액: {quote.market_cap}
            대비부호: {quote.sign}
            위험도: {quote.risk}
            거래정지: {quote.halt}
            단기과열구분: {quote.overbought}

            전일종가: {quote.prev_price}
            전일거래량: {quote.prev_volume}
            전일대비: {quote.change}

            상한가: {quote.high_limit}
            하한가: {quote.low_limit}
            거래단위: {quote.unit}
            호가단위: {quote.tick}
            소수점 자리수: {quote.decimal_places}

            통화코드: {quote.currency}
            당일환율: {quote.exchange_rate}

            당일시가: {quote.open}
            당일고가: {quote.high}
            당일저가: {quote.low}

            등락율: {quote.rate}
            대비부호명: {quote.sign_name}

            ==== 종목 지표 ====

            EPS (주당순이익): {quote.indicator.eps}
            BPS (주당순자산): {quote.indicator.bps}
            PER (주가수익비율): {quote.indicator.per}
            PBR (주가순자산비율): {quote.indicator.pbr}

            52주 최고가: {quote.indicator.week52_high}
            52주 최저가: {quote.indicator.week52_low}
            52주 최고가 날짜: {quote.indicator.week52_high_date.strftime("%Y-%m-%d")}
            52주 최저가 날짜: {quote.indicator.week52_low_date.strftime("%Y-%m-%d")}
            """

    def chart_summary(self, stock_code_or_symbol: str, *args, **kwargs) -> str:
        stock_data = self._client.stock(stock_code_or_symbol)
        chart = stock_data.chart(*args, **kwargs)

        rows = []
        for b in chart.bars:
            rows.append(
                pd.DataFrame(
                    {
                        "시간": b.time,
                        "시가": b.open,
                        "고가": b.high,
                        "저가": b.low,
                        "종가": b.close,
                        "거래량": b.volume,
                        "거래대금": b.amount,
                        "변동": b.change,
                    },
                    index=[0],
                )
            )
        return pd.concat(rows).to_csv()


def get_trader(use_virtual_trade: bool = True) -> Trader:
    return Trader(use_virtual_trade)
