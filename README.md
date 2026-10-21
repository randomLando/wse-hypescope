# WSE HypeScope

## Project Overview
**WSE HypeScope** is an open-source fundamental research dashboard and automated fact-checker for equities listed on the **Warsaw Stock Exchange (GPW / WSE)**. It evaluates corporate financial vulnerability to an AI market correction by comparing infrastructure spending (**Capital Expenditure / CapEx**) against cash retention (**Free Cash Flow / FCF**), combined with AI-powered earnings transcript analysis.

---

## The Problem: Is There an AI Bubble?
* **The CapEx vs. Revenue Gap:** Hundreds of billions flow into data centers, chips and power infrastructure, while end-user/enterprise software revenue lags behind. Much of the growth is circular (hyperscalers funding startups that buy their cloud compute).
* **The Fundamental Layer:** Unlike the 2000 dot-com bubble (unprofitable companies), today's buildout is led by highly profitable firms funding infrastructure from free cash flow, with real productivity gains.
* **Likely Outcome:** A valuation correction and consolidation rather than AI disappearing. Triggers: CapEx deceleration if enterprise ROI is delayed, startup shakeouts, the end of subsidized API pricing.
* **Key Signal:** Rising CapEx combined with shrinking FCF (`FCF = Operating Cash Flow - |CapEx|`) means growing vulnerability to a correction.

---

## Watchlist & Ecosystem Layers
All tickers use the `.WA` suffix for `yfinance`:
* **Infrastructure & Enablers:** Asbis (`ASB.WA`) *(trades in PLN on GPW, files financial statements in USD)*
* **Enterprise SaaS & AI Adopters:** Text SA (`TXT.WA`), DataWalk (`DAT.WA`), cyber_Folks (`CBF.WA`)
* **Power & Grid Bottlenecks:** Tauron (`TPE.WA`), PGE (`PGE.WA`)

---

## Data Sources
The dashboard automatically aggregates and cross-validates data from two primary financial sources:
* **Stooq ([stooq.pl](https://stooq.pl))**:
  * Scrapes and caches live constituent lists for Warsaw Stock Exchange benchmark indices (**WIG20**, **mWIG40**, **sWIG80**, and **WIG**).
  * Supplies canonical company names and validates GPW ticker codes against active market listings.
  * Ensures up-to-date benchmark lineups without manual ticker roster maintenance.
* **Yahoo Finance ([yfinance](https://github.com/ranaroussi/yfinance))**:
  * Fetches historical quarterly cash flow statements: **Capital Expenditure (CapEx)**, **Free Cash Flow (FCF)**, and **Operating Cash Flow (OCF)**.
  * Queries real-time foreign exchange rates (**`PLN=X`**) to convert foreign reporting currencies (e.g. USD for Asbis) into PLN.
  * Supplements the directory with active GPW `.WA` equities using Yahoo's live WSE equity screener.

---

## Financial Data Rules
1. **Safe Row Access:** Never index raw DataFrames directly with `.loc["Capital Expenditure"]` without fallback logic. Smaller WSE companies may omit rows in specific quarters.
2. **Outflow Normalization:** CapEx values from `yfinance` are usually negative. Apply `.abs()` so spending appears as a positive figure for chart comparisons.
3. **Currency Conversion:** Inspect `ticker.info.get("financialCurrency")` and convert USD reporting (e.g., Asbis) to **PLN**.
4. **Normalized Ratios:** Calculate percentage metrics (e.g., `CapEx as % of Operating Cash Flow`) to compare firms of different sizes. Ratios are only computed when Operating Cash Flow is positive.

---

## Roadmap

### Version 1.0 — Visual Cash-Burn Tracker
* **Stack:** Python 3.15, `yfinance`, `pandas`, `streamlit`
* **Deliverables:**
  * `test_data.py` — data extraction & cleaning validation
  * `app.py` — interactive Streamlit dashboard with ticker selection and bar charts

### Version 2.0 — AI Hype vs. Facts Reader
* **Stack:** Google GenAI SDK (Gemini API), `pydantic`
* **Deliverables:**
  * Transcript & ESPI report text parser
  * Structured classification of executive claims (quantified revenue vs. vague marketing hype)
  * Hype vs. Fact score embedded in the dashboard

### Version 3.0 — Production & Automation
* **Stack:** `duckdb`, GitHub Actions
* **Deliverables:**
  * Local DuckDB analytical database for historical metrics
  * Daily data ingestion pipeline via GitHub Actions
  * Live web deployment on a custom domain

---

## Development Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python test_data.py
```
