import yfinance as yf
import pandas as pd

# Watchlist for Warsaw Stock Exchange (WSE / GPW)
TICKERS = {
    "Text SA": "TXT.WA",
    "cyber_Folks": "CBF.WA",
    "DataWalk": "DAT.WA",
    "Asbis": "ASB.WA",
    "Tauron": "TPE.WA",
    "PGE": "PGE.WA"
}

def safe_get_metric(cashflow_df, row_name):
    """Safely fetch a row from yfinance cashflow DataFrame without crashing on missing rows."""
    if cashflow_df is not None and not cashflow_df.empty and row_name in cashflow_df.index:
        return cashflow_df.loc[row_name]
    return None

def get_usd_pln_rate(fallback_rate=4.0):
    """Fetch the latest USD/PLN exchange rate from Yahoo Finance."""
    try:
        hist = yf.Ticker("PLN=X").history(period="5d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except Exception as e:
        print(f"Warning: Could not fetch live USD/PLN rate ({e}). Using fallback {fallback_rate}.")
    return fallback_rate

def analyze_wse_ticker(name, symbol):
    print(f"\n==========================================")
    print(f" Fetching data for {name} ({symbol})")
    print(f"==========================================")
    
    ticker = yf.Ticker(symbol)
    
    # Both .info and .quarterly_cashflow make network calls -> protect both
    try:
        # Check reporting currency
        currency = ticker.info.get("financialCurrency", "PLN")
        # Get quarterly cashflow statement
        cf = ticker.quarterly_cashflow
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return

    print(f"Reporting Currency: {currency}")
    fx_rate = get_usd_pln_rate() if currency == "USD" else 1.0
    if currency == "USD":
        print(f"Converting USD -> PLN at rate: {fx_rate:.4f}")

    if cf is None or cf.empty:
        print("No quarterly cash flow data returned.")
        return

    capex = safe_get_metric(cf, "Capital Expenditure")
    fcf = safe_get_metric(cf, "Free Cash Flow")
    op_cash = safe_get_metric(cf, "Operating Cash Flow")
    
    if capex is not None:
        capex_m_pln = (capex.abs() * fx_rate / 1_000_000).round(2)
        # print("\nQuarterly CapEx (M PLN):")
        # print(capex_m_pln.head(4))
    else:
        print("\nCapEx row not found in financial statement.")
        capex_m_pln = None
        
    if fcf is not None:
        fcf_m_pln = (fcf * fx_rate / 1_000_000).round(2)
        # print("\nQuarterly Free Cash Flow (M PLN):")
        # print(fcf_m_pln.head(4))
    else:
        print("\nFree Cash Flow row not found in financial statement.")
        fcf_m_pln = None

    if capex is not None and op_cash is not None and not op_cash.empty:
        positive_op_cash = op_cash.where(op_cash > 0)
        capex_pct_op = ((capex.abs() / positive_op_cash) * 100).round(2)
        # print("\nCapEx as % of Operating Cash Flow:")
        # print(capex_pct_op.head(4).astype(str) + "%")
    else:
        capex_pct_op = None

    if capex_pct_op is None and fcf_m_pln is None and capex_m_pln is None:
        print("\nNot enough data to build Summary Table")
        return None

    summary_df = pd.DataFrame({
        "CapEx (M PLN)": capex_m_pln,
        "FCF (M PLN)": fcf_m_pln,
        "CapEx % of OCF": capex_pct_op
    }).head(4)
    print("\nSummary Table:")
    print(summary_df)
    return summary_df

if __name__ == "__main__":
    print("Starting WSE HypeScope Data Test...")
    all_companies = {}

    for name, symbol in TICKERS.items():
        df = analyze_wse_ticker(name, symbol)
        all_companies[name] = df
