import datetime
import json
import re
import time

from loguru import logger
import pandas as pd

from core.db import session
from core.discord import utils as discord_utils
from core.finance.dart import request as dart_request
from core.finance.kis import client as kis_client
from core.utils import args as args_utils
from core.utils import time as time_utils
from trading.database.finance import tables as data_tables
from trading.database.trade import tables as advisor_tables
from trading.model import llm

_PRICE_PATTERN = re.compile(r"\[\[(\w+):\s*([\d\.]+)\]\]")


def _as_json(response: str) -> dict:
    start_index = response.find("{")
    end_index = response.find("}")

    advice_dict = json.loads(response[start_index : end_index + 1])

    # parse and cast AI advice
    for k, v in advice_dict.items():
        if k == "financial_stability_score":
            advice_dict[k] = int(v.split("/")[0])
        if k == "growth_score":
            advice_dict[k] = int(v.split("/")[0])

    return advice_dict


def _summarize_chart(chart) -> str:
    rows = []
    if chart and chart.bars:
        for b in chart.bars:
            rows.append(
                pd.DataFrame(
                    {
                        "Time": b.time,
                        "Open": b.open,
                        "High": b.high,
                        "Low": b.low,
                        "Close": b.close,
                        "Volume": b.volume,
                        "Amount": b.amount,
                        "Change": b.change,
                    },
                    index=[0],
                )
            )

    if not rows:
        columns = ["Time", "Open", "High", "Low", "Close", "Volume", "Amount", "Change"]
        return pd.DataFrame(columns=columns).to_csv()

    return pd.concat(rows).to_csv()


@time_utils.timeit
@discord_utils.monitor
def main(
    read_database: str = "finance",
    write_database: str = "trade",
    date: datetime.date = time_utils.now().date(),
    top_k: int = 30,
):
    bot = llm.load_financial_bot()
    candidates = []
    raw_responses = []
    with session.get_database_session(read_database) as db_session:
        corp_quotes = (
            db_session.query(data_tables.CorporateQuote, data_tables.CorporateInfo)
            .outerjoin(
                data_tables.CorporateInfo, data_tables.CorporateQuote.symbol == data_tables.CorporateInfo.stock_code
            )
            .filter(data_tables.CorporateQuote.market_cap >= 500)
            .filter(data_tables.CorporateQuote.eps > 0)
            .filter(data_tables.CorporateQuote.rate > 0)
            .filter(data_tables.CorporateQuote.risk == "none")
            .filter(data_tables.CorporateQuote.overbought == "0")
            .filter((0.5 <= data_tables.CorporateQuote.per) & (data_tables.CorporateQuote.per <= 10))
            .filter((0.5 <= data_tables.CorporateQuote.pbr) & (data_tables.CorporateQuote.pbr <= 5))
            .filter(data_tables.CorporateQuote.eps / data_tables.CorporateQuote.bps >= 0.1)
            .order_by(data_tables.CorporateQuote.market_cap.desc())
            .all()
        )
        logger.info(f"Inspecting {min(len(corp_quotes), top_k)} stocks...")

        for quote_obj, info_obj in corp_quotes[:top_k]:
            if not info_obj or not info_obj.corp_code or not info_obj.stock_code:
                continue

            try:
                corp_code = info_obj.corp_code
                stock_code = info_obj.stock_code

                finance_report = dart_request.get_financial_report(corp_code)
                if not finance_report:
                    continue

                finance_report_df = finance_report.as_dataframe()

                chart_data_csv = _summarize_chart(
                    kis_client.get_chart(
                        stock_code,
                        start=time_utils.get_months_before(date, 6),
                        end=date,
                    )
                )
                quote_summary_text = quote_obj.summary()

                prompt = (
                    f"This is csv report of company name {info_obj.corp_name}\n"
                    f"{finance_report_df.to_csv()}\n"
                    f"This is summary of stock quote:\n{quote_summary_text}\n"
                    f"This is bar chart csv data over last 6 months:\n{chart_data_csv}"
                )

                response_content = bot.invoke(prompt).content
                data = _as_json(response_content)
                data.update(
                    {
                        "corp_name": info_obj.corp_name,
                        "corp_code": info_obj.corp_code,
                        "stock_code": info_obj.stock_code,
                        "date": date.strftime("%Y-%m-%d"),
                    }
                )

                raw_responses.append(data)

                candidates_dict = {k: v for k, v in data.items() if k != "summary"}
                candidates.append(advisor_tables.StockCandidate(**candidates_dict))

                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Error processing {info_obj.corp_name} ({info_obj.stock_code}): {e}")
                continue

        discord_messages = []
        for i, data in enumerate(raw_responses):
            discord_messages.append(
                f"회사: {data['corp_name']}\n"
                f"종목 코드: {data['stock_code']}\n"
                f"재무건전성: {data['financial_stability_score']}\n"
                f"성장지수: {data['growth_score']}\n"
                f"매수지표: {data['valuation_attractiveness']}\n"
                f"지지선(lower bound): {data['support_price']}\n"
                f"저항선(upper bound): {data['resistance_price']}\n"
                f"기술적 판단: {data['technical_signal']}\n"
                f"AI 요약: {data['summary']}"
            )

        discord_utils.send_messages(discord_messages)

    with session.get_database_session(write_database) as db_session:
        db_session.add_all(candidates)

    logger.info(f"Uploaded {len(candidates)} items to {write_database}.{advisor_tables.StockCandidate.__tablename__}")


if __name__ == "__main__":
    opts = args_utils.BasicDBTaskArguments().parse()
    main(read_database=opts.database)
