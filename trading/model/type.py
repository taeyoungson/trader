import enum
import pydantic


class Currency(enum.StrEnum):
    KRW = "KRW"
    USD = "USD"


class StockCandidate(pydantic.BaseModel):
    stock_code: str
    buy_price: float
    target_price: float
    stop_price: float


