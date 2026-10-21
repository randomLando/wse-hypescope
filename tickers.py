"""
WSE HypeScope - Equity Directory & Index Lineups.

Data Sources:
- Stooq (stooq.pl): Primary source for live WIG20, mWIG40, sWIG80, and WIG constituents & company names.
- BiznesRadar (biznesradar.pl): Live fallback scraper for index constituent tables.
- Yahoo Finance (yfinance): Live WSE equity screener for active .WA secondary listings.
"""

from concurrent.futures import ThreadPoolExecutor
import io
import re
import pandas as pd
import streamlit as st
import yfinance as yf
from yfinance import EquityQuery
from curl_cffi import requests as cf_requests

# Only our 7 project-thesis companies are kept here for the "AI, SaaS & Power (Core)" tab.
# All index lineups (WIG20, mWIG40, sWIG80) and company names are fetched live from Stooq / BiznesRadar / Yahoo!
CORE_BENCHMARK_TICKERS = {
    "Text SA": "TXT.WA",
    "cyber_Folks": "CBF.WA",
    "DataWalk": "DAT.WA",
    "Asbis": "ASB.WA",
    "Tauron": "TPE.WA",
    "PGE": "PGE.WA",
    "Orlen": "PKN.WA",
}


def clean_company_name(raw_name, symbol):
    """Strip technical exchange tags like 'C.XWAR PLN' and legal suffixes from a raw company name."""
    code = symbol.replace(".WA", "")
    if not raw_name:
        return code

    cleaned = re.sub(r"\bC\.XWAR\s*PLN\b", "", str(raw_name), flags=re.IGNORECASE)
    cleaned = re.sub(r"\bSpółka Akcyjna\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bSpolka Akcyjna\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+\bS\.?A\.?\b\.?$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,.-")
    if not cleaned:
        return code
    return cleaned


def _is_valid_equity_code(code):
    """Return True only if 'code' is a real GPW company ticker, not an index (like WIG20, MWIG40, SWIG80, WIG)."""
    c = code.strip().upper()
    if c.startswith(("WIG", "MWIG", "SWIG", "NCINDEX")):
        return False
    # GPW company symbols are 3 alphanumeric characters (or 4 for SVRS)
    return bool(re.match(r"^[A-Z0-9]{3}$", c) or c == "SVRS")


def _fetch_stooq_page(stooq_index_code, page):
    """Fetch a single Stooq index constituent page and return {sym: clean_name}."""
    page_components = {}
    url = (
        f"https://stooq.pl/q/i/?s={stooq_index_code}&l={page}"
        if page > 1
        else f"https://stooq.pl/q/i/?s={stooq_index_code}"
    )
    try:
        resp = cf_requests.get(url, impersonate="chrome", timeout=6)
        if resp.status_code != 200:
            return page_components

        # Match Stooq table rows: <a href="q/?s=pko">PKO</a>...<td ...>PKO BP</td>
        row_matches = re.findall(
            r'href="q/\?s=([a-z0-9]{2,6})">([A-Z0-9]{2,6})</a></td><td[^>]*>([^<]+)</td>',
            resp.text,
            flags=re.IGNORECASE,
        )
        if not row_matches:
            # Fallback via pandas.read_html if table attributes changed
            tables = pd.read_html(io.StringIO(resp.text))
            for tbl in tables:
                cols = [str(c).lower() for c in tbl.columns]
                if any("symbol" in c for c in cols) and any("nazwa" in c for c in cols):
                    sym_col = next(c for c in tbl.columns if "symbol" in str(c).lower())
                    name_col = next(c for c in tbl.columns if "nazwa" in str(c).lower())
                    for _, row in tbl.iterrows():
                        code = str(row[sym_col]).strip().upper()
                        name = str(row[name_col]).strip()
                        if _is_valid_equity_code(code) and name and name.lower() != "nan":
                            page_components[f"{code}.WA"] = clean_company_name(name, f"{code}.WA")
        else:
            for _, code, name in row_matches:
                code_up = code.strip().upper()
                if _is_valid_equity_code(code_up):
                    sym = f"{code_up}.WA"
                    page_components[sym] = clean_company_name(name.strip(), sym)
    except Exception:
        pass
    return page_components


def _fetch_stooq_index_components(stooq_index_code, max_pages=1):
    """
    Fetch live index constituents (Symbol -> Clean Name) directly from Stooq.pl's index component pages:
    e.g. https://stooq.pl/q/i/?s=wig20, mwig40, swig80, wig
    """
    if max_pages <= 1:
        return _fetch_stooq_page(stooq_index_code, 1)

    components = {}
    with ThreadPoolExecutor(max_workers=min(max_pages, 8)) as executor:
        futures = [executor.submit(_fetch_stooq_page, stooq_index_code, p) for p in range(1, max_pages + 1)]
        for fut in futures:
            components.update(fut.result())
    return components


def _fetch_biznesradar_index_components(br_index_name):
    """
    Backup live fetcher from BiznesRadar index pages (WIG20, mWIG40, sWIG80, WIG).
    Extracts both the GPW ticker code and the company name from the live index table.
    """
    url = f"https://www.biznesradar.pl/gielda/indeks:{br_index_name}"
    components = {}
    try:
        resp = cf_requests.get(url, impersonate="chrome", timeout=6)
        if resp.status_code == 200:
            # Links on BiznesRadar look like: <a class="s-name" href="/notowania/..." title="...">PKO (PKO BP)</a> or >CDR</a>
            matches = re.findall(
                r'href="/notowania/([^"#]+)(?:#[^"]*)?"[^>]*>([A-Z0-9]{2,5})(?:\s*\(([^)]+)\))?</a>',
                resp.text,
            )
            for slug, code, paren_name in matches:
                code_up = code.strip().upper()
                if not _is_valid_equity_code(code_up):
                    continue
                sym = f"{code_up}.WA"
                display_name = paren_name.strip() if paren_name else slug.replace("-", " ").title()
                components[sym] = clean_company_name(display_name, sym)
    except Exception:
        pass
    return components


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_live_index_components(index_name):
    """
    Fetch live {company_name: 'SYMBOL.WA'} for a GPW index ('WIG20', 'mWIG40', 'sWIG80', 'WIG')
    from Stooq.pl first, then BiznesRadar as backup.
    """
    stooq_map = {
        "WIG20": ("wig20", 1),
        "mWIG40": ("mwig40", 1),
        "sWIG80": ("swig80", 2),
        "WIG": ("wig", 8),
    }
    stooq_code, pages = stooq_map[index_name]
    sym_to_name = _fetch_stooq_index_components(stooq_code, max_pages=pages)

    if len(sym_to_name) < 5:
        sym_to_name = _fetch_biznesradar_index_components(index_name)

    # Convert {sym: name} -> {name: sym} with unique keys
    result = {}
    for sym, name in sym_to_name.items():
        key = name if name not in result else f"{name} ({sym.replace('.WA', '')})"
        result[key] = sym
    return result


def _fetch_yahoo_wse_screener():
    """Fetch active WSE quotes from Yahoo Finance Screener concurrently across pages."""
    query = EquityQuery("eq", ["exchange", "WSE"])
    all_quotes = []
    try:
        first_res = yf.screen(
            query,
            size=250,
            offset=0,
            sortField="intradaymarketcap",
            sortAsc=False,
        )
        if isinstance(first_res, dict):
            all_quotes.extend(first_res.get("quotes", []))
            total = first_res.get("total", 0)
            remaining_offsets = [off for off in (250, 500) if off < total]
            if remaining_offsets:
                with ThreadPoolExecutor(max_workers=len(remaining_offsets)) as executor:
                    futures = [
                        executor.submit(
                            yf.screen,
                            query,
                            size=250,
                            offset=off,
                            sortField="intradaymarketcap",
                            sortAsc=False,
                        )
                        for off in remaining_offsets
                    ]
                    for fut in futures:
                        res = fut.result()
                        if isinstance(res, dict):
                            all_quotes.extend(res.get("quotes", []))
    except Exception as e:
        print(f"Warning: Yahoo Screener supplement failed ({e}).")
    return all_quotes


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_live_wse_tickers(_cache_version=2):
    """
    Build the full live WSE company directory (cached 24h):
    1. Pulls live WIG20, mWIG40, sWIG80, and WIG constituents & clean names from Stooq.pl / BiznesRadar in parallel.
    2. Supplements with Yahoo Finance's live WSE Screener concurrently for any additional active '.WA' equities.
    """
    tickers = {}
    seen_symbols = set()
    indices = ("WIG20", "mWIG40", "sWIG80", "WIG")

    with ThreadPoolExecutor(max_workers=5) as executor:
        idx_futures = {idx: executor.submit(fetch_live_index_components, idx) for idx in indices}
        screener_future = executor.submit(_fetch_yahoo_wse_screener)

        # 1. Pull live WSE companies with clean names from Stooq / BiznesRadar in index order
        for idx in indices:
            idx_companies = idx_futures[idx].result()
            for name, sym in idx_companies.items():
                code = sym.replace(".WA", "").upper()
                if _is_valid_equity_code(code) and sym not in seen_symbols:
                    seen_symbols.add(sym)
                    tickers[name] = sym

        # 2. Supplement with Yahoo Finance live WSE Screener
        quotes = screener_future.result()
        for q in quotes:
            symbol = q.get("symbol", "")
            code = symbol.replace(".WA", "").upper()
            if not symbol or not symbol.endswith(".WA") or symbol in seen_symbols or not _is_valid_equity_code(code):
                continue
            raw_name = q.get("longName") or q.get("displayName") or q.get("shortName") or symbol
            name = clean_company_name(raw_name, symbol)
            if name in tickers:
                name = f"{name} ({code})"
            seen_symbols.add(symbol)
            tickers[name] = symbol

    for name, sym in CORE_BENCHMARK_TICKERS.items():
        code = sym.replace(".WA", "").upper()
        if _is_valid_equity_code(code) and sym not in seen_symbols:
            seen_symbols.add(sym)
            tickers[name] = sym

    return tickers


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_live_index_presets(_cache_version=2):
    """
    Dynamically fetch the live lineups for WIG20, mWIG40, and sWIG80 from Stooq.pl / BiznesRadar.
    No hardcoded index constituent lists!
    """
    presets = {}
    fallback_slices = {"WIG20": (0, 20), "mWIG40": (20, 60), "sWIG80": (60, 140)}
    ordered_items = None

    with ThreadPoolExecutor(max_workers=3) as executor:
        idx_futures = {
            idx_name: executor.submit(fetch_live_index_components, idx_name)
            for idx_name in fallback_slices
        }
        for idx_name, (start, end) in fallback_slices.items():
            live_idx = idx_futures[idx_name].result()
            clean_idx = {
                name: sym for name, sym in live_idx.items()
                if _is_valid_equity_code(sym.replace(".WA", ""))
            }
            if len(clean_idx) >= 10:
                presets[idx_name] = clean_idx
            else:
                if ordered_items is None:
                    ordered_items = list(fetch_live_wse_tickers().items())
                presets[idx_name] = dict(ordered_items[start:end])

    presets["AI, SaaS & Power (Core)"] = CORE_BENCHMARK_TICKERS
    return presets


def format_dropdown_options():
    """Return a dict mapping 'Company Name (SYMBOL.WA)' -> (name, symbol) from live WSE directory."""
    live_tickers = fetch_live_wse_tickers()
    return {
        f"{name} ({sym})": (name, sym)
        for name, sym in live_tickers.items()
        if _is_valid_equity_code(sym.replace(".WA", ""))
    }
