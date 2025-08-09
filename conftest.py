import pytest
import pytest_mock
import sqlalchemy
from sqlalchemy import orm

from core.db import config as db_config
from trading.database import base

_TEST_DATABASE = "test"


@pytest.fixture(scope="function")
def test_db(mocker: pytest_mock.MockerFixture):
    config = db_config.load_config()

    try:
        engine = sqlalchemy.create_engine(f"{config.dsn}/{_TEST_DATABASE}")
        base.Base.metadata.create_all(engine)
        session = orm.Session(bind=engine)
        mocker.patch("core.db.session.get_or_create_engine", return_value=engine)

        yield session

        session.close()
        base.Base.metadata.drop_all(engine)

    except Exception as e:
        print(f"Connecting to mysql failed with dsn: {config.dsn}/{_TEST_DATABASE}, did you 'make infra'?")
        raise e
