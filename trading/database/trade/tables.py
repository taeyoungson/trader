from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import orm
from sqlalchemy import String

from core.db import session

_DATABASE: str = "trade"


class Base(orm.DeclarativeBase):
    pass


class StockCandidate(Base):
    __tablename__ = "candidate_stock"

    id = Column(Integer, primary_key=True, autoincrement=True)
    corp_code = Column(String(8))
    corp_name = Column(String(150))
    stock_code = Column(String(6))
    buy_price = Column(Float)
    target_price = Column(Float)
    stop_price = Column(Float)
    date = Column(String(10))


class Purchase(Base):
    __tablename__ = "purchase"

    id = Column(Integer, primary_key=True, autoincrement=True)
    buy_price = Column(Float)
    target_price = Column(Float)
    stop_price = Column(Float)


session.register_tables(Base, database=_DATABASE)
