import datetime

import lightweight_charts
from loguru import logger

from core.db import session
from core.finance.kis import client as kis_client
from core.utils import args as args_utils
from core.utils import indicator as indicator_utils
from core.utils import time as time_utils
from trading.database import base
from trading.database.finance import build_corporate_info
from trading.database.finance import build_corporate_quote
from trading.database.trade import build_candidate_stock
from trading.database.trade import tables as trade_tables


def _setup(database: str = "test") -> None:
    engine = session.get_or_create_engine(database)
    base.Base.metadata.create_all(engine)
    logger.info("Test database initialized")


def _teardown(database: str = "test") -> None:
    engine = session.get_or_create_engine(database)
    base.Base.metadata.drop_all(engine)
    logger.info("Test database cleaned up")


def _visualize(candidate_stock: trade_tables.StockCandidate, date: datetime.date) -> None:
    stock_code = candidate_stock.stock_code
    support_price = candidate_stock.support_price
    resistent_price = candidate_stock.resistance_price

    start = time_utils.get_months_before(date, 6)
    end = time_utils.get_months_after(date, 6)

    chart_view = lightweight_charts.Chart(width=1280, height=720)
    chart = kis_client.get_chart(stock_code, start=start, end=end)

    chart_view.set(chart.df())

    chart_view.set_visible_range(start, end)
    fallback_prices = indicator_utils.get_finbonacci_fallback(support_price, resistent_price)

    chart_view.horizontal_line(support_price, text="support price")
    chart_view.horizontal_line(resistent_price, text="resistent price")
    chart_view.horizontal_line(fallback_prices[0], text="buy price")
    chart_view.vertical_line(date, text="start")

    chart_view.show(block=True)


def main(database: str, start_date: datetime.date, end_date: datetime.date):
    logger.info(
        f"Backtest started at {time_utils.DateTimeFormatter.DATETIME_FULL.format(time_utils.now())}"
        f"with following arguments: \n"
        f"\t database: {database}\n"
        f"\t start_date: {start_date}\n"
        f"\t end_date: {end_date}\n"
    )
    try:
        _setup(database=database)
        build_corporate_info.main(database=database)
        build_corporate_quote.main(database=database)
        build_candidate_stock.main(read_database=database, write_database=database, date=start_date)

        with session.get_database_session(database) as db_session:
            candidate_stocks = db_session.query(trade_tables.StockCandidate).all()

            for c in candidate_stocks:
                _visualize(c, date=start_date)

    except Exception as e:
        logger.error(e)
        raise e
    finally:
        _teardown(database=database)


if __name__ == "__main__":
    opts = args_utils.BacktestArguments.parse()

    database = opts.database
    start_date = opts.start_date
    window = opts.window

    main(
        database,
        start_date,
        time_utils.get_days_after(start_date, window),
    )
