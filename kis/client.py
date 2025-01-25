from kis import config as kis_config
import pykis
from loguru import logger


def load(use_virtual_trade: bool) -> pykis.PyKis:
    config = kis_config.load_config()

    if use_virtual_trade:
        return pykis.PyKis(
            id=config.id,
            account=config.account,
            appkey=config.app_key,
            secretkey=config.secret_key,
            virtual_id=config.virtual_id,
            virtual_appkey=config.virtual_app_key,
            virtual_secretkey=config.virtual_secret_key,
            keep_token=True,
        )

    logger.warning("!!! Using LIVE trading system !!!")
    return pykis.PyKis(
        id=config.id,
        account=config.account,
        appkey=config.app_key,
        secretkey=config.secret_key,
        keep_token=True,
    )


if __name__ == "__main__":
    kis = load(use_virtual_trade=False)
    breakpoint()
    logger.info(kis.account().balance())
