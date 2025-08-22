import datetime
import io
import zipfile

from loguru import logger
import requests
import xmltodict

from core.finance.dart import config
from core.finance.dart import model
from core.finance.dart import url
from core.utils import time as time_utils


def _load_crtfc_key() -> str:
    cred = config.load_config()
    return cred.crtfc_key


def get_corp_item_lists(url_key: str = "corp_code") -> list[model.CorpInfoItem]:
    crtfc_key = _load_crtfc_key()

    resp = requests.get(
        url=url.get_url_by_name(url_key),
        params={"crtfc_key": crtfc_key},
        timeout=10,
    )
    zip_binary = io.BytesIO(resp.content)
    with zipfile.ZipFile(zip_binary) as zf:
        xml_bytes = zf.read("CORPCODE.xml")

    xml_str = xml_bytes.decode("utf-8")
    data = xmltodict.parse(xml_str)["result"]["list"]

    corp_item_lists = [model.CorpInfoItem(**item) for item in data]
    return corp_item_lists


def _is_corp_name_exists(corp_name_or_corp_eng_name: str) -> bool:
    corp_codes = get_corp_item_lists()
    for corp_code in corp_codes:
        if corp_code.corp_name == corp_name_or_corp_eng_name or corp_code.corp_eng_name == corp_name_or_corp_eng_name:
            return True
    return False


def get_corp_code_by_name(name: str) -> str:
    assert _is_corp_name_exists(name)
    corp_codes = get_corp_item_lists()
    for corp_code in corp_codes:
        if corp_code.corp_name == name or corp_code.corp_eng_name == name:
            return corp_code.corp_code
    raise ValueError(f"Cannot find corp_code by name: {name}")


def get_stock_code_by_name(name: str) -> str:
    assert _is_corp_name_exists(name)
    corp_codes = get_corp_item_lists()
    for corp_code in corp_codes:
        if corp_code.corp_name == name or corp_code.corp_eng_name == name:
            return corp_code.stock_code
    raise ValueError(f"Cannot find stock_code by name: {name}")


def _resolve_reprt_code(date: datetime.date) -> model.ReportCode:
    """
    First quarter report should be online until May 15th.
    Second quarter report should be online until August 14th.
    Third quarter report should be online until November 14th.
    Fourth quarter report should be online until March 31st next year.
    """
    year = date.year

    if datetime.date(year, 3, 31) <= date <= datetime.date(year, 5, 14):
        return model.ReportCode.FOURTH_QUARTER

    elif date <= datetime.date(year, 8, 14):
        return model.ReportCode.FIRST_QUARTER

    elif date <= datetime.date(year, 11, 14):
        return model.ReportCode.SECOND_QUARTER

    else:
        return model.ReportCode.THIRD_QUARTER


def get_financial_report(
    corp_code: str,
    fs_div: model.ReportType = model.ReportType.CONSOLIDATED.value,
    url_key: str = "finance",
    date: datetime.date = time_utils.now().date(),
) -> model.FinancialReport | None:
    crtfc_key = _load_crtfc_key()

    reprt_code = _resolve_reprt_code(date)
    next_year = date.year + 1 if reprt_code == model.ReportCode.THIRD_QUARTER else date.year

    for code, bsns_year in [
        (reprt_code.next(), next_year),
        (reprt_code, date.year),
    ]:
        try:
            resp = requests.get(
                url=url.get_url_by_name(url_key),
                params={
                    "crtfc_key": crtfc_key,
                    "corp_code": corp_code,
                    "bsns_year": str(bsns_year),
                    "reprt_code": code.value,
                    "fs_div": fs_div,
                },
                timeout=30,
            )

            resp.raise_for_status()
            data = resp.json()

            if data["status"] == "000":
                items = [model.FinancialReportItem(**item) for item in resp.json()["list"]]
                logger.info(f"{bsns_year} {code.name} financial report loaded for {corp_code}")
                return model.FinancialReport(items)

        except (requests.exceptions.RequestException, KeyError) as e:
            raise e
    logger.warning(f"Failed to load financial report for corp_code: {corp_code}")
    return None
