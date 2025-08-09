from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String

from trading.database import base

_DATABASE: str = "trade"


class StockCandidate(base.Base):
    __tablename__ = "candidate_stock"
    __bind_key__ = _DATABASE

    id = Column(Integer, primary_key=True, autoincrement=True)
    corp_code = Column(String(8))
    corp_name = Column(String(150))
    stock_code = Column(String(6))
    buy_price = Column(Float)
    target_price = Column(Float)
    stop_price = Column(Float)
    date = Column(String(10))


class Purchase(base.Base):
    __tablename__ = "purchase"
    __bind_key__ = _DATABASE

    id = Column(Integer, primary_key=True, autoincrement=True)
    buy_price = Column(Float)
    target_price = Column(Float)
    stop_price = Column(Float)
