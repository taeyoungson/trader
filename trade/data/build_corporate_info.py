from loguru import logger

from core.db import session
from core.db import utils as db_utils
from core.finance.dart import request as dart_request
from core.scheduler import instance
from core.scheduler import jobs
from trade.data import tables


@instance.DefaultBackgroundScheduler.scheduled_job(
    jobs.TriggerType.CRON, id="build_corportate_info", day_of_week="0", hour=5
)
def build_corporate_info(database: str = "finance"):
    corp_info_lists = dart_request.get_corp_item_lists()
    corp_infos = [item.model_dump() for item in corp_info_lists]

    db_engine = session.get_or_create_engine(database)
    with db_engine.begin() as conn:
        upsert_stmt = db_utils.auto_upsert_stmt(tables.CorporateInfo, corp_infos)
        conn.execute(upsert_stmt)

    logger.info(f"Upserted {len(corp_infos)} items to {database}.{tables.CorporateInfo.__tablename__}")
