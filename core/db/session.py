import contextlib

import sqlalchemy
from sqlalchemy import orm

from core.db import config

_engines: dict[str, sqlalchemy.Engine] = {}

_POOL_SIZE = 10
_POOL_TIMEOUT = 60
_POOL_RECYCLE = 3600


def get_or_create_engine(database: str, echo: bool = False) -> sqlalchemy.Engine:
    global _engines

    if database not in _engines:
        db_config = config.load_config()
        dsn = db_config.dsn.rstrip("/")
        db_name = database.lstrip("/")
        url = f"{dsn}/{db_name}"

        _engines[database] = sqlalchemy.create_engine(
            url,
            echo=echo,
            pool_size=_POOL_SIZE,
            pool_timeout=_POOL_TIMEOUT,
            pool_recycle=_POOL_RECYCLE,
        )

    return _engines[database]


@contextlib.contextmanager
def get_database_session(database: str) -> orm.Session:
    engine = get_or_create_engine(database)
    session = orm.Session(bind=engine)

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
