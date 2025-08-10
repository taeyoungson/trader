"""pipeline script for manual execution"""

import argparse

from loguru import logger

from core.utils import args as args_utils
from core.utils import time as time_utils
from trading.database.finance import build_corporate_info
from trading.database.finance import build_corporate_quote
from trading.database.trade import build_candidate_stock


@time_utils.timeit
def main(opts: argparse.Namespace):
    finance_db = opts.finance_database
    trade_db = opts.trade_database
    top_k = opts.top_k

    logger.info(
        f"Manual data pipeline job started at {time_utils.DateTimeFormatter.DATETIME_FULL.format(time_utils.now())}"
    )

    if not opts.skip_info:
        build_corporate_info.main(database=finance_db)

    if not opts.skip_quote:
        build_corporate_quote.main(database=finance_db)

    build_candidate_stock.main(read_database=finance_db, write_database=trade_db, top_k=top_k)


if __name__ == "__main__":
    opts = args_utils.PipelineTaskArguments.parse()
    main(opts)
