import pydantic


class DartURL(pydantic.BaseModel):
    name: str
    url: str


_BASE_URL: DartURL = DartURL(name="base", url="https://opendart.fss.or.kr/api/")
_CORP_CODE_URL: DartURL = DartURL(name="corp_code", url="https://opendart.fss.or.kr/api/corpCode.xml")
_FINANCE_URL: DartURL = DartURL(name="finance", url="https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json")


_URLS: list[DartURL] = [
    _BASE_URL,
    _CORP_CODE_URL,
    _FINANCE_URL,
]

_URL_MAP: dict[str, DartURL] = {url.name: url.url for url in _URLS}


def get_url_by_name(name: str) -> str:
    assert name in _URL_MAP, f"{name} is not in url_map!, {_URL_MAP}"
    return _URL_MAP[name]
