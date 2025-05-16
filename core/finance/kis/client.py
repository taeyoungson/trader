from loguru import logger
import pykis

from core.finance.kis import config as kis_config

_PYKIS_CLIENT = None


def get_client(use_virtual_trade: bool = True) -> pykis.PyKis:
    global _PYKIS_CLIENT
    if _PYKIS_CLIENT:
        return _PYKIS_CLIENT

    cfg = kis_config.load_config()

    if use_virtual_trade:
        logger.warning("!!! Using VIRTUAL trading system !!!")
        _client = pykis.PyKis(
            id=cfg.virtual_id,
            account=cfg.virtual_account,
            appkey=cfg.virtual_app_key,
            secretkey=cfg.virtual_secret_key,
            keep_token=True,
        )
    else:
        logger.warning("!!! Using LIVE trading system !!!")
        _client = pykis.PyKis(
            id=cfg.id,
            account=cfg.account,
            appkey=cfg.app_key,
            secretkey=cfg.secret_key,
            keep_token=True,
        )
    _PYKIS_CLIENT = _client
    return _PYKIS_CLIENT
