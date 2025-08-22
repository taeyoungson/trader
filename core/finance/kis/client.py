import functools
import time
from typing import Callable

from loguru import logger
import pykis
from pykis.responses import exceptions
from requests import exceptions as request_exceptions

from core.finance.kis import config as kis_config

_PYKIS_CLIENT = None
_DELAY = 0.2


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


def _make_delayed_request_until_succeeds(fn: Callable):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        delay = _DELAY
        try:
            while True:
                try:
                    return fn(*args, **kwargs)
                except request_exceptions.ConnectionError:
                    time.sleep(delay)
                    delay *= 2
                except exceptions.KisNotFoundError:
                    return None
        except Exception as e:
            raise e

    return wrapper


def buy(stock: pykis.KisStock, *args, **kwargs):
    try:
        stock.buy(*args, **kwargs)
    except exceptions.KisMarketNotOpenedError:
        logger.warning("Market not open!")


@_make_delayed_request_until_succeeds
def get_account() -> pykis.KisAccount:
    _client = _load_client()
    return _client.account()


@_make_delayed_request_until_succeeds
def get_stock(symbol: str) -> pykis.KisStock | None:
    _client = _load_client()
    return _client.stock(symbol)


@_make_delayed_request_until_succeeds
def get_quote(symbol: str) -> pykis.KisQuote | None:
    stock = get_stock(symbol)

    if not stock:
        return None

    return stock.quote()


@_make_delayed_request_until_succeeds
def get_chart(symbol: str, *args, **kwargs) -> pykis.KisChart | None:
    stock = get_stock(symbol)

    if not stock:
        return None

    return stock.chart(*args, **kwargs)
