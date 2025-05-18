from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import orm
from sqlalchemy import String

from core.db import session

_DATABASE: str = "finance"


class Base(orm.DeclarativeBase):
    pass


class CorporateInfo(Base):
    __tablename__ = "corporate_info"

    corp_code = Column(String(8), primary_key=True)
    corp_name = Column(String(150))
    corp_eng_name = Column(String(150))
    stock_code = Column(String(6))
    modify_date = Column(String(8))


class CorporateQuote(Base):
    __tablename__ = "corporate_quote"

    symbol = Column(String(6), primary_key=True)
    market = Column(String(10))
    sector_name = Column(String(30))

    price = Column(Float, nullable=True)
    volume = Column(BigInteger, nullable=True)
    amount = Column(BigInteger, nullable=True)
    market_cap = Column(BigInteger, nullable=True)

    sign = Column(String(10), nullable=True)
    sign_name = Column(String(20), nullable=True)
    risk = Column(String(50), nullable=True)
    halt = Column(Boolean, nullable=True)
    overbought = Column(String(50), nullable=True)

    prev_price = Column(Float, nullable=True)
    prev_volume = Column(BigInteger, nullable=True)

    change = Column(Float, nullable=True)
    rate = Column(Float, nullable=True)
    high_limit = Column(Float, nullable=True)
    low_limit = Column(Float, nullable=True)
    unit = Column(Integer, nullable=True)
    tick = Column(Float, nullable=True)
    decimal_places = Column(Integer, nullable=True)

    currency = Column(String(10), nullable=True)
    exchange_rate = Column(Float, nullable=True)

    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)

    eps = Column(Float, nullable=True)
    bps = Column(Float, nullable=True)
    per = Column(Float, nullable=True)
    pbr = Column(Float, nullable=True)

    week52_high = Column(Float, nullable=True)
    week52_low = Column(Float, nullable=True)
    week52_high_date = Column(Date, nullable=True)
    week52_low_date = Column(Date, nullable=True)

    def summary(self) -> str:
        summary_lines = [
            f"Stock Quote Summary for Symbol: {self.symbol}",
            f"Market: {self.market}, Sector: {self.sector_name}",
            f"Current Price: {self.price} {self.currency if self.currency else ''}",
            f"Change: {self.change} ({self.rate}%) - Sign: {self.sign_name}",
            f"Day's Range: {self.low_price} - {self.high_price} (Open: {self.open_price})",
            f"Volume: {self.volume}, Trading Value (Amount): {self.amount}",
            f"Market Cap: {self.market_cap}",
            f"Previous Close: {self.prev_price}",
            f"Risk Status: {self.risk}, Trading Halt: {'Yes' if self.halt else 'No'}, Overbought Status: {self.overbought}",
            "--- Key Indicators ---",
            f"EPS (Earnings Per Share): {self.eps}",
            f"BPS (Book-value Per Share): {self.bps}",
            f"PER (Price to Earnings Ratio): {self.per}",
            f"PBR (Price to Book-value Ratio): {self.pbr}",
            "--- 52-Week Range ---",
            f"52-Week High: {self.week52_high} (on {self.week52_high_date})",
            f"52-Week Low: {self.week52_low} (on {self.week52_low_date})",
        ]
        return "\n".join(summary_lines)


session.register_tables(Base, database=_DATABASE)
