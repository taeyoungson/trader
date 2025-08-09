import re

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


def main(read_database: str = "finance", write_database: str = "trade"):
    bot = llm.load_financial_bot()
    candidates = []
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
            .filter((0.5 <= data_tables.CorporateQuote.per) & (data_tables.CorporateQuote.per <= 5))
            .filter((0.5 <= data_tables.CorporateQuote.pbr) & (data_tables.CorporateQuote.pbr <= 5))
            .order_by(data_tables.CorporateQuote.rate.desc())
            .all()
        )

        now = time_utils.now()
        for quote_obj, info_obj in corp_quotes:
            if not info_obj or not info_obj.corp_code or not info_obj.stock_code:
                continue

            corp_code = info_obj.corp_code
            stock_code = info_obj.stock_code

            finance_report = dart_request.get_financial_report(corp_code)
            if not finance_report:
                continue

            finance_report_df = finance_report.as_dataframe()

            chart_data_csv = _summarize_chart(
                kis_client.get_chart(
                    stock_code,
                    start=time_utils.get_months_before(now, 6),
                    end=now,
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

            data = {}
            for match in _PRICE_PATTERN.finditer(response_content):
                price_type = match.group(1)
                price_value = float(match.group(2))
                data[price_type] = price_value

            if not data:
                continue

            data.update(
                {
                    "corp_name": info_obj.corp_name,
                    "corp_code": info_obj.corp_code,
                    "stock_code": info_obj.stock_code,
                    "date": now.strftime("%Y-%m-%d"),
                }
            )
            candidates.append(advisor_tables.StockCandidate(**data))

        if candidates:
            discord_message_header = f"📈 **New Stock Candidates for {time_utils.now().strftime('%Y-%m-%d')}** ({len(candidates)} found out of {len(corp_quotes)}) 📈\n"
            discord_messages = [discord_message_header]
            for i, c in enumerate(candidates):
                message = (
                    f"--- Candidate {i + 1} ---\n"
                    f"🏢 **Company**: {c.corp_name} ({c.stock_code})\n"
                    f"💰 **Buy Price**: {c.buy_price:,.0f}\n"
                    f"🎯 **Target Price**: {c.target_price:,.0f}\n"
                    f"🛑 **Stop Price**: {c.stop_price:,.0f}\n"
                )
                discord_messages.append(message)

            full_discord_message = "\n".join(discord_messages)
            discord_utils.send(full_discord_message)

    with session.get_database_session(write_database) as db_session:
        db_session.add_all(candidates)

    logger.info(f"Uploaded {len(candidates)} items to {write_database}.{advisor_tables.StockCandidate.__tablename__}")


if __name__ == "__main__":
    opts = args_utils.BasicDBTaskArguments().parse()
    main(read_database=opts.database)
