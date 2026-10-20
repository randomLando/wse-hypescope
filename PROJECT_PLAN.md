# WSE HypeScope: Project Blueprint & Context

## Project Overview
**WSE HypeScope** is an open-source fundamental research dashboard and automated fact-checker built for analyzing equities listed on the **Warsaw Stock Exchange (GPW / WSE)**. It evaluates corporate financial vulnerability to an AI market correction by comparing infrastructure spending (**Capital Expenditure / CapEx**) against cash retention (**Free Cash Flow / FCF**), combined with AI-powered earnings transcript analysis.

---

## Investment Thesis: Is There an AI Bubble?
* **The CapEx vs. Revenue Gap:** Hundreds of billions flow into data centers, chips and power infrastructure, while end-user/enterprise software revenue lags behind. Much of the growth is circular (hyperscalers funding startups that buy their cloud compute).
* **The Fundamental Layer:** Unlike the 2000 dot-com bubble (unprofitable companies), today's buildout is led by highly profitable firms funding infrastructure from free cash flow, with real productivity gains.
* **Likely Outcome:** A valuation correction and consolidation rather than AI disappearing. Triggers: CapEx deceleration if enterprise ROI is delayed, startup shakeouts, the end of subsidized API pricing.
* **Key Signal:** Rising CapEx combined with shrinking FCF (`FCF = Operating Cash Flow - |CapEx|`) means growing vulnerability to a correction.

---

## Ecosystem Layers (GPW Mapping)
* **Layer 2 — Infrastructure & Enablers:** Asbis (`ASB.WA`)
* **Layer 3 — Enterprise SaaS & Adopters:** Text SA (`TXT.WA`), DataWalk (`DAT.WA`), cyber_Folks (`CBF.WA`)
* **Layer 4 — Power & Land Bottlenecks:** Tauron (`TPE.WA`), PGE (`PGE.WA`)

*(Layer 1 — US hyperscalers — is out of scope: not listed on GPW.)*

---

## Target Equities (WSE Watchlist)
All tickers use the `.WA` suffix for `yfinance`:
* **SaaS & AI Adopters:** Text SA (`TXT.WA`), cyber_Folks (`CBF.WA`), DataWalk (`DAT.WA`)
* **IT Hardware & Distribution:** Asbis (`ASB.WA`) *(Note: Trades in PLN on GPW, files financial statements in USD)*
* **Power & Energy Grid:** Tauron (`TPE.WA`), PGE (`PGE.WA`)

---

## Technical Constraints & Financial Data Rules
1. **Safe Row Access:** Never index raw DataFrames directly with `.loc["Capital Expenditure"]` without fallback logic. Smaller WSE companies may omit rows in specific quarters.
2. **Outflow Normalization:** CapEx values from `yfinance` are usually negative. Apply `.abs()` so spending appears as a positive figure for bar chart comparisons.
3. **Currency Conversion:** Dynamically inspect `ticker.info.get("financialCurrency")` to convert USD reporting (e.g., Asbis) to **PLN**.
4. **Normalized Ratios:** Calculate percentage metrics (e.g., `CapEx as % of Operating Cash Flow`) to normalize comparison between domestic firms.

---

## Project Roadmap

### Phase 1: First Semester — Version 1.0 (Visual Cash-Burn Tracker)
* **Stack:** Python 3.15, `yfinance`, `pandas`, `streamlit`
* **Deliverables:**
  * `test_data.py` (Data extraction & cleaning validation)
  * `app.py` (Interactive Streamlit dashboard with ticker selection and bar charts)

### Phase 2: Winter Break — Version 2.0 (AI Hype vs. Facts Reader)
* **Stack:** Google GenAI SDK (Gemini API), `pydantic`
* **Deliverables:**
  * Transcript & ESPI report text parser
  * Structured classification of executive claims (quantified revenue vs. vague marketing hype)
  * Hype vs. Fact sentiment score embedded in Streamlit

### Phase 3: Second Semester — Version 3.0 (Production & Automation)
* **Stack:** `duckdb`, GitHub Actions, custom `.me` domain
* **Deliverables:**
  * Local DuckDB analytical database for historical metrics
  * Daily background ingestion pipeline via GitHub Actions
  * Live web deployment with custom domain from GitHub Student Developer Pack

---

## AI Assistant Working Mode
* **Tutor Mode / Strict Review Mode:** Guide step-by-step and explain concepts; no full autonomous code dumps.
* The student writes the core logic; agents may help with boilerplate, tests and code review.

---

## Developer Environment Guidelines
* **Virtual Environment:** `.venv` (Activate via `source .venv/bin/activate` on macOS)
* **Git Security:** Ensure `.venv`, `.env`, and `__pycache__` are listed in `.gitignore`.
