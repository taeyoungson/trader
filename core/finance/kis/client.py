from loguru import logger
import pykis

from core.finance.kis import config as kis_config

_PYKIS_CLIENT = None


def _load_client() -> pykis.PyKis:
    global _PYKIS_CLIENT
    if _PYKIS_CLIENT is not None:
        return _PYKIS_CLIENT

    cfg = kis_config.load_config()
    if cfg.use_virtual_trade:
        _PYKIS_CLIENT = pykis.PyKis(
            id=cfg.virtual_id,
            account=cfg.virtual_account,
            appkey=cfg.virtual_app_key,
            secretkey=cfg.virtual_secret_key,
            keep_token=True,
        )
    logger.warning("Initializing Live Trade client")
    _PYKIS_CLIENT = pykis.PyKis(
        id=cfg.id,
        account=cfg.account,
        appkey=cfg.app_key,
        secretkey=cfg.secret_key,
        keep_token=True,
    )
    return _PYKIS_CLIENT


def get_account() -> pykis.KisAccount:
    return _load_client().account()


def get_stock(symbol: str) -> pykis.KisStock:
    return _load_client().stock(symbol)


def get_quote(symbol: str) -> pykis.KisQuote:
    return _load_client().stock(symbol).quote()


def get_chart(symbol: str, *args, **kwargs) -> pykis.KisChart:
    return _load_client().stock(symbol).chart(*args, **kwargs)
