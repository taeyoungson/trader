from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from trading.database import base

_DATABASE: str = "trade"


class StockCandidate(base.Base):
    __tablename__ = "candidate_stock"
    __bind_key__ = _DATABASE

    stock_code = Column(String(6), primary_key=True)
    corp_code = Column(String(8))
    corp_name = Column(String(150))
    financial_stability_score = Column(Integer)
    growth_score = Column(Integer)
    valuation_attractiveness = Column(String(30))
    support_price = Column(Integer)
    resistance_price = Column(Integer)
    technical_signal = Column(String(40))
    date = Column(String(10))
