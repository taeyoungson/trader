from loguru import logger
from pykis.responses import exceptions
import tqdm

from core.db import session
from core.db import utils as db_utils
from core.finance.kis import client as kis_client
from core.scheduler import instance
from core.scheduler import jobs
from trading.database.finance import tables


@instance.DefaultBackgroundScheduler.scheduled_job(
    jobs.TriggerType.CRON, id="build_corportate_quote", day_of_week="0, 1, 2, 3, 4", hour=16
)
def build_corporate_quote(database: str = "finance", market: str = "KRX"):
    corp_quotes = []
    with session.get_database_session(database) as db_session:
        corps_with_stock_codes = db_session.query(tables.CorporateInfo).filter(tables.CorporateInfo.stock_code).all()

        for corp in tqdm.tqdm(corps_with_stock_codes, desc="Getting quote data..."):
            try:
                quote = kis_client.get_quote(corp.stock_code, market)

            except exceptions.KisNotFoundError:
                logger.warning(f"corp {corp.corp_name} with code {corp.stock_code} not found")
                continue

            quote_data = {
                "symbol": quote.symbol,
                "market": quote.market,
                "sector_name": quote.sector_name,
                "price": quote.price,
                "volume": quote.volume,
                "amount": quote.amount,
                "market_cap": quote.market_cap,
                "sign": quote.sign,
                "sign_name": quote.sign_name,
                "risk": quote.risk,
                "halt": quote.halt,
                "overbought": quote.overbought,
                "prev_price": quote.prev_price,
                "prev_volume": quote.prev_volume,
                "change": quote.change,
                "rate": quote.rate,
                "high_limit": quote.high_limit,
                "low_limit": quote.low_limit,
                "unit": quote.unit,
                "tick": quote.tick,
                "decimal_places": quote.decimal_places,
                "currency": quote.currency,
                "exchange_rate": quote.exchange_rate,
                "open_price": quote.open,
                "high_price": quote.high,
                "low_price": quote.low,
                "eps": quote.indicator.eps if quote.indicator else None,
                "bps": quote.indicator.bps if quote.indicator else None,
                "per": quote.indicator.per if quote.indicator else None,
                "pbr": quote.indicator.pbr if quote.indicator else None,
                "week52_high": quote.indicator.week52_high if quote.indicator else None,
                "week52_low": quote.indicator.week52_low if quote.indicator else None,
                "week52_high_date": quote.indicator.week52_high_date
                if quote.indicator and quote.indicator.week52_high_date
                else None,
                "week52_low_date": quote.indicator.week52_low_date
                if quote.indicator and quote.indicator.week52_low_date
                else None,
            }
            corp_quotes.append(quote_data)

    with session.get_or_create_engine(database).begin() as conn:
        upsert_stmt = db_utils.auto_upsert_stmt(tables.CorporateQuote, corp_quotes)
        conn.execute(upsert_stmt)

    logger.info(f"Upserted {len(corp_quotes)} items to {database}.{tables.CorporateQuote.__tablename__}")
