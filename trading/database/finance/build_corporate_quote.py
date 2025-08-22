from loguru import logger
import tqdm

from core.db import session
from core.db import utils as db_utils
from core.discord import utils as discord_utils
from core.finance.kis import client as kis_client
from core.utils import args as args_utils
from core.utils import time as time_utils
from trading.database.finance import tables


@time_utils.timeit
@discord_utils.monitor
def main(database: str = "finance", top_k: int = -1):
    corp_quotes = []
    with session.get_database_session(database) as db_session:
        corps_with_stock_codes = db_session.query(tables.CorporateInfo).filter(tables.CorporateInfo.stock_code).all()

        logger.info(f"Getting quotes for the number of {len(corps_with_stock_codes)} companies")

        if top_k == -1:
            top_k = len(corps_with_stock_codes)

        for corp in tqdm.tqdm(corps_with_stock_codes[:top_k], desc="Getting quote data..."):
            quote = kis_client.get_quote(corp.stock_code)

            if not quote:
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


if __name__ == "__main__":
    task_args = args_utils.BasicDBTaskArguments().parse()
    main(task_args.database)
