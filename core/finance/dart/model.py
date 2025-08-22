import enum

import pandas as pd
import pydantic


class ReportCode(enum.Enum):
    FIRST_QUARTER = "11013"
    SECOND_QUARTER = "11012"
    THIRD_QUARTER = "11014"
    FOURTH_QUARTER = "11011"

    def next(self):
        members = list(self.__class__)

        current_index = members.index(self)
        next_index = (current_index + 1) % len(members)

        return members[next_index]


class CorpInfoItem(pydantic.BaseModel):
    corp_code: str
    corp_name: str
    corp_eng_name: str | None
    stock_code: str | None
    modify_date: str  # format: (yyyymmdd)


class ReportType(enum.StrEnum):
    SEPARATE = "OFS"
    CONSOLIDATED = "CFS"


class RequestBase(pydantic.BaseModel):
    pass


class FinancialReportRequest(RequestBase):
    crtfc_key: str
    corp_code: str
    bsns_year: str
    reprt_code: ReportType


class FinancialReportItem(pydantic.BaseModel):
    rcept_no: str
    reprt_code: str
    bsns_year: str
    corp_code: str
    sj_div: str
    sj_nm: str
    account_id: str
    account_nm: str
    account_detail: str | None
    thstrm_nm: str | None
    thstrm_amount: str | None
    thstrm_add_amount: str | None = None
    frmtrm_nm: str | None = None
    frmtrm_amount: str | None = None
    frmtrm_q_nm: str | None = None
    frmtrm_q_amount: str | None = None
    frmtrm_add_amount: str | None = None
    bfefrmtrm_nm: str | None = None
    bfefrmtrm_amount: str | None = None
    ord: int
    currency: str


class FinancialReport:
    def __init__(self, items: list[FinancialReportItem]):
        self._items = items

    @property
    def items(self) -> list[FinancialReportItem]:
        return self._items

    def as_dataframe(self):
        return pd.DataFrame([item.model_dump() for item in self._items])
