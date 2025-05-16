import functools
import io
import zipfile

from loguru import logger
import requests
import xmltodict

from core.finance.dart import config
from core.finance.dart import model
from core.finance.dart import url
from core.utils import time as time_utils


@functools.cache
def _load_crtfc_key() -> str:
    cred = config.load_config()
    return cred.crtfc_key


@functools.cache
def _get_corp_codes(url_key: str = "corp_code") -> list[model.CorpInfoItem]:
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


@functools.cache
def _is_corp_name_exists(corp_name_or_corp_eng_name: str) -> bool:
    corp_codes = _get_corp_codes()
    for corp_code in corp_codes:
        if corp_code.corp_name == corp_name_or_corp_eng_name or corp_code.corp_eng_name == corp_name_or_corp_eng_name:
            return True
    return False


@functools.cache
def get_corp_code_by_name(name: str) -> str:
    assert _is_corp_name_exists(name)
    corp_codes = _get_corp_codes()
    for corp_code in corp_codes:
        if corp_code.corp_name == name or corp_code.corp_eng_name == name:
            return corp_code.corp_code
    raise ValueError(f"Cannot find corp_code by name: {name}")


@functools.cache
def get_stock_code_by_name(name: str) -> str:
    assert _is_corp_name_exists(name)
    corp_codes = _get_corp_codes()
    for corp_code in corp_codes:
        if corp_code.corp_name == name or corp_code.corp_eng_name == name:
            return corp_code.stock_code
    raise ValueError(f"Cannot find corp_code by name: {name}")


def get_financial_report(
    name: str,
    num_requests_reports: int = 2,
    fs_div: model.ReportType = model.ReportType.CONSOLIDATED.value,
    url_key: str = "finance",
) -> model.FinancialReport:
    crtfc_key = _load_crtfc_key()

    year = time_utils.now().year
    report_items = []

    for bsns_year in range(year, year - num_requests_reports, -1):
        for reprt_code in [
            model.ReportCode.FOURTH_QUARTER.value,
            model.ReportCode.THIRD_QUARTER.value,
            model.ReportCode.SECOND_QUARTER.value,
            model.ReportCode.FIRST_QUARTER.value,
        ]:
            try:
                resp = requests.get(
                    url=url.get_url_by_name(url_key),
                    params={
                        "crtfc_key": crtfc_key,
                        "corp_code": get_corp_code_by_name(name),
                        "bsns_year": str(bsns_year),
                        "reprt_code": reprt_code,
                        "fs_div": fs_div,
                    },
                    timeout=30,
                )

                resp.raise_for_status()
                data = resp.json()

                if data["status"] == "000":
                    items = [model.FinancialReportItem(**item) for item in resp.json()["list"]]
                    report_items.extend(items)
                    logger.info(f"{bsns_year} {reprt_code} financial report loaded for {name}")
                    return model.FinancialReport(report_items)

            except (requests.exceptions.RequestException, KeyError) as e:
                raise e
    raise ValueError(f"Failed to load financial report for {name}")
