import contextlib

import sqlalchemy
from sqlalchemy import orm

from core.db import config

_engines: dict[str, sqlalchemy.Engine] = {}


def get_or_create_engine(database: str) -> sqlalchemy.Engine:
    if database not in _engines:
        db_config = config.load_config()
        dsn = db_config.dsn.rstrip("/")
        db_name = database.lstrip("/")
        url = f"{dsn}/{db_name}"
        _engines[database] = sqlalchemy.create_engine(url, echo=True)
    return _engines[database]


def register_tables(tables_base: orm.DeclarativeBase, database: str):
    engine = get_or_create_engine(database)
    tables_base.metadata.create_all(engine)
    print(f"Tables registered/ensured in database '{database}'.")


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
