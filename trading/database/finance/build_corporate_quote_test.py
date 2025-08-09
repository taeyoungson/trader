import pytest_mock
from sqlalchemy import orm

from core.finance.dart import model as dart_model
from trading.database.finance import build_corporate_info
from trading.database.finance import tables

_TEST_DB = "test"
_TEST_CORPORATE_INFO = [
    dart_model.CorpInfoItem(
        corp_code="000000",
        corp_name="test_corp",
        corp_eng_name="test_corp_eng",
        stock_code="000000",
        modify_date="20250801",
    ),
    dart_model.CorpInfoItem(
        corp_code="111111",
        corp_name="test_corp_2",
        corp_eng_name="test_corp_eng_2",
        stock_code="111111",
        modify_date="20250801",
    ),
]
_TEST_CORPORATE_QUOTES = []


def test_build_corporate_info(
    mocker: pytest_mock.MockerFixture,
    test_db: orm.Session,
):
    mocker.patch("core.finance.dart.request.get_corp_item_lists", return_value=_TEST_CORPORATE_INFO)

    build_corporate_info.main()

    result_in_db = test_db.query(tables.CorporateInfo).all()
    result_in_db.sort(key=lambda x: x.corp_code)

    assert len(result_in_db) == len(_TEST_CORPORATE_INFO)

    for i, elem in enumerate(result_in_db):
        assert elem.corp_code == _TEST_CORPORATE_INFO[i].corp_code
        assert elem.corp_name == _TEST_CORPORATE_INFO[i].corp_name
        assert elem.corp_eng_name == _TEST_CORPORATE_INFO[i].corp_eng_name
        assert elem.stock_code == _TEST_CORPORATE_INFO[i].stock_code
        assert elem.modify_date == _TEST_CORPORATE_INFO[i].modify_date
