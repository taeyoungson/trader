from loguru import logger

from core.db import session
from core.db import utils as db_utils
from core.discord import utils as discord_utils
from core.finance.dart import request as dart_request
from core.utils import args as args_utils
from core.utils import time as time_utils
from trading.database.finance import tables


@time_utils.timeit
@discord_utils.monitor
def main(database: str = "finance"):
    corp_infos = [item.model_dump() for item in dart_request.get_corp_item_lists()]

    db_engine = session.get_or_create_engine(database)
    with db_engine.begin() as conn:
        upsert_stmt = db_utils.auto_upsert_stmt(tables.CorporateInfo, corp_infos)
        conn.execute(upsert_stmt)

    logger.info(f"Upserted {len(corp_infos)} items to {database}.{tables.CorporateInfo.__tablename__}")


if __name__ == "__main__":
    task_args = args_utils.BasicDBTaskArguments().parse()
    main(task_args.database)
