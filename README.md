# Automated Stock Trading Bot

This project is an automated trading bot designed to analyze and trade stocks on the Korea Exchange (KRX) using the Korea Investment & Securities (KIS) API.

![Stock Candidates Example](./assets/candidate.png)

---

## Overview

The bot operates in a fully automated cycle, preparing data and executing trades based on a predefined schedule.

### Workflow

1. **Data Synchronization (Weekly)**
   - **Schedule:** Every Monday at 5:00 AM.
   - **Task:** Fetches a comprehensive list of all publicly listed corporations from DART and stores it in the `CorporateInfo` table.

2. **Market Data Collection (Daily)**
   - **Schedule:** Every weekday at 4:00 PM.
   - **Task:** Retrieves the day's closing quotes for all companies in the master list and saves them to the `CorporateQuote` table.

3. **Candidate Selection (Daily)**
   - **Schedule:** Every weekday at 7:00 AM.
   - **Task:** Filters promising companies based on fundamental metrics, analyzes them using an LLM, and stores the final candidates in the database.

4. **Automated Trading (Daily)**
   - **Schedule:** Every weekday from 9:00 AM to 3:30 PM.
   - **Task:** Monitors the market and executes buy orders via the KIS API if a stock's price hits its entry point.

---

## Technology Stack

- **Language:** Python 3.11
- **Package Management:** uv
- **Key Libraries:**
  - **LLM Integration:** LangChain, Langchain-OpenAI
  - **Financial APIs:** python-kis, DART requests
  - **Scheduling:** APScheduler
  - **Data Handling:** Pandas
  - **Database:** SQLAlchemy, mysqlclient

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/taeyoungson/trader.git
   cd trader
   ```

2. **Set Up Virtual Environment:**
   ```bash
   uv sync
   source .venv/bin/activate
   ```

3. **Configure Environment:**
   - Set up environment variables for the database connection, KIS API keys, and OpenAI API key in a `.env` file.

---

## Docker Setup

- **Database Service:**
  - Uses MySQL 8.0 with a custom configuration and initialization scripts.
  - Environment variables for MySQL user and password are required.

- **Application Service:**
  - Built using the Dockerfile in the `docker` directory.
  - Depends on the database service.

## Makefile Commands

- **Start Database:**
  ```bash
  make db
  ```

- **Start Application:**
  ```bash
  make start-app
  ```

- **Teardown Application:**
  ```bash
  make teardown-app
  ```

- **Apply Alembic Migrations:**
  ```bash
  make apply-alembic
  ```

## Project Structure

- **Core Components:**
  - `core/bot`: Handles bot client and configuration.
  - `core/db`: Manages database sessions and utilities.
  - `core/discord`: Integrates with Discord for notifications.
  - `core/finance`: Interfaces with financial data sources.
  - `core/rss`: Manages RSS feed utilities.
  - `core/scheduler`: Manages job scheduling.

- **Trading Components:**
  - `trading/asset`: Manages asset-related functionalities.
  - `trading/backtest`: Contains backtesting pipeline.
  - `trading/database`: Manages database interactions and configurations.
  - `trading/model`: Contains models for trading logic.
  - `trading/runners`: Executes trading strategies.
  - `trading/strategy`: Defines trading strategies.
