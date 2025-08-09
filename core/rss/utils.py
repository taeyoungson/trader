import time

import feedparser
from loguru import logger

from core.rss import urls

_ETAG = None
_MODIFIED = None


def _log_metadata(feed: feedparser.FeedParserDict):
    logger.info("--- 피드 정보 ---")
    logger.info(f"제목: {feed.feed.get('title', 'N/A')}")
    logger.info(f"링크: {feed.feed.get('link', 'N/A')}")
    logger.info(f"설명: {feed.feed.get('subtitle', feed.feed.get('description', 'N/A'))}")
    logger.info(f"업데이트: {feed.feed.get('updated', 'N/A')}")
    logger.info(f"총 항목 수: {len(feed.entries)}")
    logger.info("-" * 30)


def invoke(url: str):
    global _ETAG, _MODIFIED
    feed = feedparser.parse(url, etag=_ETAG, modified=_MODIFIED)

    if feed.status == 304:
        logger.info("콘텐츠 변경 없음: 캐시된 버전을 사용합니다.")
        return

    if feed.bozo:
        logger.warning(f"경고: RSS 피드 파싱 중 오류 발생 ({url}): {feed.bozo_exception}")

    if hasattr(feed, "etag") and feed.etag:
        _ETAG = feed.etag
        logger.debug(f"새로운 ETag 저장: {_ETAG}")

    if hasattr(feed, "modified") and feed.modified:
        _MODIFIED = feed.modified
        logger.debug(f"새로운 Last-Modified 저장: {_MODIFIED}")

    _log_metadata(feed)

    logger.info("--- 최신 항목 ---")
    for entry in feed.entries:
        logger.info(f"  제목: {entry.get('title', 'N/A')}")
        logger.info(f"  링크: {entry.get('link', 'N/A')}")

        published_time = "N/A"
        if entry.get("published_parsed"):
            published_time = time.strftime("%Y-%m-%d %H:%M:%S", entry.published_parsed)
        logger.info(f"  발행일: {published_time}")

        summary = entry.get("summary", "N/A")
        if entry.get("summary_detail") and entry.summary_detail.type == "text/plain":
            summary = entry.summary_detail.value

        logger.info(f"  요약: {summary[:200]}...")  # 처음 200자만 출력
        logger.info("-" * 20)


print(invoke(urls.INVESTING_CO_STOCK_MARKET))
