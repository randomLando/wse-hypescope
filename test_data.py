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

    if cf is None or cf.empty:
        print("No quarterly cash flow data returned.")
        return

    capex = safe_get_metric(cf, "Capital Expenditure")
    fcf = safe_get_metric(cf, "Free Cash Flow")
    op_cash = safe_get_metric(cf, "Operating Cash Flow")
    
    if capex is not None:
        capex_abs = capex.abs()
        print("\nQuarterly CapEx (Outflow in positive numbers):")
        print(capex_abs.head(4))
    else:
        print("\nCapEx row not found in financial statement.")
        
    if fcf is not None:
        print("\nQuarterly Free Cash Flow:")
        print(fcf.head(4))
    else:
        print("\nFree Cash Flow row not found in financial statement.")
        
    if capex is not None and op_cash is not None and not op_cash.empty:
        capex_pct_op = (capex.abs() / op_cash.abs()) * 100
        print("\nCapEx as % of Operating Cash Flow:")
        print(capex_pct_op.head(4).round(2).astype(str) + "%")

if __name__ == "__main__":
    print("Starting WSE HypeScope Data Test...")
    for name, symbol in TICKERS.items():
        analyze_wse_ticker(name, symbol)
