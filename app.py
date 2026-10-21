from concurrent.futures import ThreadPoolExecutor
import datetime
import importlib
import json
import streamlit as st
import yfinance as yf
import pandas as pd

import ui
importlib.reload(ui)
from ui import (
    format_cashflow_table,
    render_top_banner,
    render_section_header,
    render_quarter_summary,
    render_footer,
)
from tickers import (
    CORE_BENCHMARK_TICKERS,
    fetch_live_index_presets,
    format_dropdown_options,
)

st.set_page_config(page_title="WSE HypeScope", page_icon="🔭", layout="wide")

_CASHFLOW_KEY_MAP = {
    "quarterlyCapitalExpenditure": "Capital Expenditure",
    "quarterlyFreeCashFlow": "Free Cash Flow",
    "quarterlyOperatingCashFlow": "Operating Cash Flow",
}


def safe_get_metric(cashflow_df, row_name):
    """Safely fetch a row from yfinance cashflow DataFrame without crashing on missing rows."""
    if cashflow_df is not None and not cashflow_df.empty and row_name in cashflow_df.index:
        return cashflow_df.loc[row_name]
    return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_usd_pln_rate(fallback_rate=4.0):
    """Fetch the latest USD/PLN exchange rate from Yahoo Finance."""
    try:
        hist = yf.Ticker("PLN=X").history(period="5d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except Exception as e:
        print(f"Warning: Could not fetch live USD/PLN rate ({e}). Using fallback {fallback_rate}.")
    return fallback_rate


def _fetch_quarterly_cashflow_and_currency(ticker, symbol):
    """
    Fetch only the 3 required quarterly cashflow series and reporting currency
    in a single Yahoo Finance fundamentals-timeseries request (instead of 4 requests).
    Falls back to ticker.quarterly_cashflow if needed.
    """
    currency = None
    cf = None
    try:
        start_dt = int(datetime.datetime(2021, 1, 1).timestamp())
        end_dt = int(pd.Timestamp.now("UTC").ceil("D").timestamp())
        types_str = ",".join(_CASHFLOW_KEY_MAP.keys())
        ts_url = (
            f"https://query2.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{symbol}"
            f"?symbol={symbol}&type={types_str}&period1={start_dt}&period2={end_dt}"
        )
        resp = ticker._data.cache_get(url=ts_url)
        data = json.loads(resp.text)
        result = (data.get("timeseries") or {}).get("result") or []

        rows = {}
        all_dates = set()
        for item in result:
            for raw_key, row_label in _CASHFLOW_KEY_MAP.items():
                points = item.get(raw_key)
                if not isinstance(points, list):
                    continue
                series_map = {}
                for pt in points:
                    if not isinstance(pt, dict):
                        continue
                    if currency is None and pt.get("currencyCode"):
                        currency = pt.get("currencyCode")
                    as_of = pt.get("asOfDate")
                    val = (pt.get("reportedValue") or {}).get("raw")
                    if as_of is not None and val is not None:
                        ts = pd.Timestamp(as_of)
                        series_map[ts] = float(val)
                        all_dates.add(ts)
                if series_map:
                    rows[row_label] = series_map

        if rows and all_dates:
            sorted_dates = sorted(all_dates, reverse=True)
            cf = pd.DataFrame.from_dict(rows, orient="index", columns=sorted_dates).astype("float")
    except Exception:
        cf = None

    if cf is None or cf.empty:
        cf = ticker.quarterly_cashflow

    if not currency:
        try:
            fin_res = ticker._quote._fetch(modules=["financialData"])
            fin_data = (((fin_res or {}).get("quoteSummary") or {}).get("result") or [{}])[0].get("financialData") or {}
            currency = fin_data.get("financialCurrency", "PLN")
        except Exception:
            currency = "PLN"

    return cf, currency or "PLN"


@st.cache_data(ttl=3600, show_spinner=False)
def analyze_wse_ticker(name, symbol):
    ticker = yf.Ticker(symbol)

    # Both .info and .quarterly_cashflow make network calls -> protect both
    try:
        cf, currency = _fetch_quarterly_cashflow_and_currency(ticker, symbol)
    except Exception as e:
        return

    fx_rate = get_usd_pln_rate() if currency == "USD" else 1.0

    if cf is None or cf.empty:
        return None

    capex = safe_get_metric(cf, "Capital Expenditure")
    fcf = safe_get_metric(cf, "Free Cash Flow")
    op_cash = safe_get_metric(cf, "Operating Cash Flow")

    if capex is not None:
        capex_m_pln = (capex.abs() * fx_rate / 1_000_000).round(2)
    else:
        capex_m_pln = None

    if fcf is not None:
        fcf_m_pln = (fcf * fx_rate / 1_000_000).round(2)
    else:
        fcf_m_pln = None

    if capex is not None and op_cash is not None and not op_cash.empty:
        positive_op_cash = op_cash.where(op_cash > 0)
        capex_pct_op = ((capex.abs() / positive_op_cash) * 100).round(2)
    else:
        capex_pct_op = None

    if capex_pct_op is None and fcf_m_pln is None and capex_m_pln is None:
        return None

    summary_df = pd.DataFrame({
        "CapEx (M PLN)": capex_m_pln,
        "FCF (M PLN)": fcf_m_pln,
        "CapEx % of OCF": capex_pct_op
    }).head(4)
    summary_df.index = summary_df.index.strftime("%Y-%m-%d")
    return summary_df


@st.cache_data(ttl=3600, show_spinner=False)
def build_benchmark_leaderboard(company_pairs):
    """Build a latest-quarter comparison table across a tuple of (name, symbol) pairs."""
    if not company_pairs:
        return None

    get_usd_pln_rate()

    latest_quarter = {}
    with ThreadPoolExecutor(max_workers=min(len(company_pairs), 16)) as executor:
        futures = [
            (name, sym, executor.submit(analyze_wse_ticker, name, sym))
            for name, sym in company_pairs
        ]
        for name, sym, fut in futures:
            company_df = fut.result()
            if company_df is not None and not company_df.empty:
                latest_quarter[f"{name} ({sym})"] = company_df.iloc[0]
    if not latest_quarter:
        return None
    return pd.DataFrame(latest_quarter).T


usd_pln = get_usd_pln_rate()
render_top_banner(usd_pln)

dropdown_map = format_dropdown_options()
index_presets = fetch_live_index_presets()
default_custom_watchlist = [
    f"{name} ({sym})"
    for name, sym in CORE_BENCHMARK_TICKERS.items()
    if f"{name} ({sym})" in dropdown_map
]

if "watchlist_selection" not in st.session_state:
    st.session_state.watchlist_selection = default_custom_watchlist
else:
    st.session_state.watchlist_selection = [
        item for item in st.session_state.watchlist_selection if item in dropdown_map
    ]


def reset_watchlist():
    st.session_state.watchlist_selection = default_custom_watchlist


ctrl_left, ctrl_mid, ctrl_right = st.columns([1.1, 0.8, 0.5], gap="small", vertical_alignment="bottom")
with ctrl_left:
    selected_choice = st.selectbox(
        "Search WSE Equity (type company name or ticker):",
        options=list(dropdown_map.keys()),
        index=0,
    )
with ctrl_mid:
    preset_options = list(index_presets.keys()) + ["Custom Watchlist"]
    selected_preset = st.selectbox(
        "Benchmark Index / Watchlist:",
        options=preset_options,
        index=0,  # WIG20 by default
    )
with ctrl_right:
    with st.popover("Edit Custom Watchlist", width="stretch"):
        st.multiselect(
            "Select companies for 'Custom Watchlist':",
            options=list(dropdown_map.keys()),
            key="watchlist_selection",
        )
        st.button("Reset Custom Watchlist", on_click=reset_watchlist)

selected_name, symbol = dropdown_map[selected_choice]
df = analyze_wse_ticker(selected_name, symbol)

if df is not None:
    col_left, col_right = st.columns([1.1, 1.3], gap="medium")
    with col_left:
        render_section_header(f"Cash Flow Statement &raquo; {selected_name} ({symbol}) — M PLN", variant="blue")
        st.table(format_cashflow_table(df))
        render_quarter_summary(df)

    with col_right:
        render_section_header(f"Quarterly Chart: {symbol} — CapEx vs. FCF (M PLN)", variant="silver")
        st.bar_chart(
            df[["CapEx (M PLN)", "FCF (M PLN)"]],
            stack=False,
            height=300,
            x_label="Quarter",
            y_label="M PLN"
        )
else:
    st.error("No financial data available for the selected company.")

if selected_preset == "Custom Watchlist":
    active_pairs = tuple(
        dropdown_map[label]
        for label in st.session_state.watchlist_selection
        if label in dropdown_map
    )
else:
    active_pairs = tuple(index_presets[selected_preset].items())

leaderboard_df = build_benchmark_leaderboard(active_pairs)
if leaderboard_df is not None:
    bot_left, bot_right = st.columns([1.1, 1.3], gap="medium")
    with bot_left:
        render_section_header(
            f"WSE {selected_preset} Leaderboard — Latest Quarter (M PLN)",
            variant="blue",
        )
        st.table(format_cashflow_table(leaderboard_df))
    with bot_right:
        render_section_header(
            f"{selected_preset} Comparison — CapEx as % of Operating Cash Flow",
            variant="silver",
        )
        st.bar_chart(
            leaderboard_df[["CapEx % of OCF"]],
            height=300,
            x_label="Company",
            y_label="CapEx % of OCF"
        )

render_footer()