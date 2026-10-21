import streamlit as st
import pandas as pd


def style_fcf(val):
    if pd.isna(val):
        return "color: #777777;"
    if val > 0:
        return "color: #008000; background-color: #e8f5e9; font-weight: bold;"
    if val < 0:
        return "color: #cc0000; background-color: #ffebee; font-weight: bold;"
    return ""


def style_ocf_pct(val):
    if pd.isna(val):
        return "color: #777777;"
    if val > 100:
        return "color: #cc0000; font-weight: bold;"
    if val < 35:
        return "color: #008000;"
    return ""


def format_cashflow_table(df):
    """Apply Stooq/Win7 number formatting and green/red cell highlights to the cashflow DataFrame."""
    return (
        df.style.format({
            "CapEx (M PLN)": "{:,.2f}",
            "FCF (M PLN)": "{:+,.2f}",
            "CapEx % of OCF": "{:.2f}%"
        }, na_rep="—")
        .map(style_fcf, subset=["FCF (M PLN)"])
        .map(style_ocf_pct, subset=["CapEx % of OCF"])
    )


def render_top_banner(usd_pln):
    """Render the glossy header banner and global control styling."""
    st.html(f"""
    <style>
    header[data-testid="stHeader"] {{
      display: none !important;
    }}
    .stMainBlockContainer, [data-testid="stAppViewBlockContainer"] {{
      padding-top: 8px !important;
      padding-left: 18px !important;
      padding-right: 18px !important;
      max-width: 100% !important;
    }}

    /* Global Typography */
    body, [data-testid="stAppViewContainer"], .stMarkdown, p, span {{
      font-family: Tahoma, "Segoe UI", Arial, sans-serif;
    }}

    /* Widget Labels (Stooq / Win7 bold 11px) */
    [data-testid="stWidgetLabel"] label,
    [data-testid="stWidgetLabel"] p {{
      font-family: Tahoma, "Segoe UI", Arial, sans-serif !important;
      font-size: 11px !important;
      font-weight: bold !important;
      color: #222222 !important;
      margin-bottom: 2px !important;
    }}

    /* Clean Glossy Buttons */
    [data-testid="stButton"] button,
    [data-testid="stPopover"] > button,
    [data-testid^="stBaseButton"] {{
      background: linear-gradient(180deg, #ffffff 0%, #f4f6f9 48%, #e2e7ef 52%, #d6dee9 100%) !important;
      border: 1px solid #9aa6b8 !important;
      border-radius: 2px !important;
      box-shadow: inset 0 1px 0 #ffffff, 0 1px 1px rgba(0, 0, 0, 0.08) !important;
      color: #111111 !important;
      font-family: Tahoma, "Segoe UI", Arial, sans-serif !important;
      font-size: 11px !important;
      font-weight: bold !important;
      text-shadow: 0 1px 0 #ffffff !important;
      padding: 4px 12px !important;
      transition: background 0.1s ease-in-out !important;
    }}

    [data-testid="stButton"] button:hover,
    [data-testid="stPopover"] > button:hover,
    [data-testid^="stBaseButton"]:hover {{
      background: linear-gradient(180deg, #f0f6fc 0%, #dce9f7 48%, #c8ddf2 52%, #d5e5f5 100%) !important;
      border-color: #5d6e87 !important;
      color: #000000 !important;
    }}

    [data-testid="stButton"] button:active,
    [data-testid="stPopover"] > button:active,
    [data-testid^="stBaseButton"]:active {{
      background: #c2d4e7 !important;
      border-color: #4a5b75 !important;
      box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2) !important;
      color: #000000 !important;
    }}

    /* Textboxes, Selectboxes & Multiselects */
    [data-testid="stTextInput"] input,
    [data-testid="stTextInputRootElement"],
    [data-baseweb="input"],
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] > div {{
      border-color: #9aa6b8 !important;
      border-radius: 2px !important;
      background-color: #ffffff !important;
      font-family: Tahoma, "Segoe UI", Arial, sans-serif !important;
      font-size: 12px !important;
    }}

    [data-testid="stTextInputRootElement"]:hover,
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] > div:hover {{
      border-color: #5d6e87 !important;
    }}

    [data-testid="stTextInputRootElement"]:focus-within,
    [data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within > div,
    [data-testid="stMultiSelect"] div[data-baseweb="select"]:focus-within > div {{
      border-color: #4a5b75 !important;
      box-shadow: 0 0 2px rgba(74, 91, 117, 0.4) !important;
    }}

    /* Multiselect Tag Chips */
    [data-baseweb="tag"] {{
      background: linear-gradient(180deg, #ffffff 0%, #eaedf2 100%) !important;
      border: 1px solid #9aa6b8 !important;
      border-radius: 2px !important;
      box-shadow: inset 0 1px 0 #ffffff !important;
    }}

    [data-baseweb="tag"] span {{
      color: #111111 !important;
      font-family: Tahoma, Arial, sans-serif !important;
      font-size: 11px !important;
    }}

    /* Popover Body Window Frame */
    [data-testid="stPopoverBody"] {{
      background: linear-gradient(180deg, #ffffff 0%, #eaedf2 100%) !important;
      border: 1px solid #9aa6b8 !important;
      border-radius: 3px !important;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.18), inset 0 1px 0 #ffffff !important;
      padding: 10px !important;
    }}

    /* Data Grid Tables */
    [data-testid="stTable"] table {{
      font-family: Tahoma, "Segoe UI", Arial, sans-serif !important;
      font-size: 11px !important;
      border-collapse: collapse !important;
      border: 1px solid #9aa6b8 !important;
      width: 100% !important;
    }}
    [data-testid="stTable"] th {{
      background: linear-gradient(180deg, #f7f9fb 0%, #dfe4ec 50%, #cdd4df 52%, #e2e7ef 100%) !important;
      color: #111111 !important;
      font-weight: bold !important;
      font-size: 11px !important;
      border: 1px solid #9aa6b8 !important;
      padding: 4px 6px !important;
      text-shadow: 0 1px 0 #ffffff !important;
    }}
    [data-testid="stTable"] td {{
      border: 1px solid #d0d7e0 !important;
      font-size: 11px !important;
      padding: 3px 6px !important;
    }}
    </style>
    <div style="font-family: Tahoma, Arial, sans-serif; font-size: 12px; color: #000; margin-bottom: 6px;">
      <div style="display: flex; align-items: baseline; justify-content: space-between; padding: 6px 2px;">
        <span style="font-family: Arial, Helvetica, sans-serif; font-size: 28px; font-weight: bold; letter-spacing: -0.5px; color: #000;">WSE HypeScope</span>
        <span style="font-size: 12px; color: #222;">Live <b>USD/PLN</b>: <span style="background: linear-gradient(180deg, #e8f8ec 0%, #c8ebd0 100%); border: 1px solid #8ec99c; color: #006600; font-weight: bold; padding: 1px 6px;">{usd_pln:.4f}</span> &nbsp;|&nbsp; Unit: <b>M PLN</b></span>
      </div>
      <div style="display: flex; justify-content: space-between; align-items: center; background: linear-gradient(180deg, #7b8da6 0%, #5d6e87 48%, #4a5b75 52%, #3f4f66 100%); color: #ffffff; padding: 6px 10px; font-weight: bold; text-shadow: 0 -1px 0 rgba(0,0,0,0.4); border-top: 1px solid #9ab0cc; border-bottom: 1px solid #2d394b;">
        <span>WSE Fundamental Research: Capital Expenditure (CapEx) vs. Free Cash Flow (FCF)</span>
        <span style="font-size: 11px; font-weight: normal; text-shadow: none;">
          Data Sources:
          <a href="https://stooq.pl" target="_blank" rel="noopener noreferrer" style="color: #ffffff; font-weight: bold; text-decoration: underline;">Stooq</a> &bull;
          <a href="https://finance.yahoo.com" target="_blank" rel="noopener noreferrer" style="color: #ffffff; font-weight: bold; text-decoration: underline;">Yahoo Finance (yfinance)</a>
        </span>
      </div>
    </div>
    """)


def render_section_header(title, variant="blue"):
    """Render a glossy section header bar ('blue' or 'silver')."""
    if variant == "blue":
        st.html(
            f'<div style="background: linear-gradient(180deg, #7b8da6 0%, #5d6e87 48%, #4a5b75 52%, #3f4f66 100%); '
            f'color:#ffffff; font-family:Tahoma,Arial,sans-serif; font-size:11px; font-weight:bold; '
            f'padding:4px 8px; border:1px solid #354357; box-shadow: inset 0 1px 0 rgba(255,255,255,0.35); '
            f'text-shadow: 0 -1px 0 rgba(0,0,0,0.4);">{title}</div>'
        )
    else:
        st.html(
            f'<div style="background: linear-gradient(180deg, #f7f9fb 0%, #dfe4ec 48%, #cdd4df 52%, #e2e7ef 100%); '
            f'color:#111111; font-family:Tahoma,Arial,sans-serif; font-size:11px; font-weight:bold; '
            f'padding:4px 8px; border:1px solid #9aa6b8; box-shadow: inset 0 1px 0 #ffffff; '
            f'text-shadow: 0 1px 0 #ffffff;">{title}</div>'
        )


def render_quarter_summary(df):
    """Render the glossy summary box below the table for the most recent quarter."""
    latest = df.iloc[0]
    fcf_val = latest["FCF (M PLN)"]
    capex_val = latest["CapEx (M PLN)"]
    ocf_pct = latest["CapEx % of OCF"]
    status_color = "#007700" if (pd.notna(fcf_val) and fcf_val > 0) else "#bb0000"
    status_label = "POSITIVE FCF (Self-Funded)" if (pd.notna(fcf_val) and fcf_val > 0) else "NEGATIVE FCF (Cash Burn)"
    st.html(f"""
    <div style="font-family:Tahoma,Arial,sans-serif; font-size:11px; background: linear-gradient(180deg, #ffffff 0%, #eaedf2 100%); border:1px solid #9aa6b8; box-shadow: inset 0 1px 0 #ffffff; padding:6px 9px; margin-top:4px;">
      <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #cfd6e0; padding-bottom:3px; margin-bottom:5px;">
        <div>
          <b>Latest Quarter Summary ({df.index[0]}):</b>
          <span style="color:{status_color}; font-weight:bold; margin-left:6px;">{status_label}</span>
        </div>
        <span style="color:#666666; font-size:10px;">Source: <b>Yahoo Finance (yfinance)</b></span>
      </div>
      <div style="display:flex; justify-content:space-between;">
        <span>CapEx: <b>{f'{capex_val:,.2f}' if pd.notna(capex_val) else '—'} M PLN</b></span>
        <span>Free Cash Flow (FCF): <b style="color:{status_color};">{f'{fcf_val:+,.2f}' if pd.notna(fcf_val) else '—'} M PLN</b></span>
        <span>CapEx / OCF: <b>{f'{ocf_pct:.2f}%' if pd.notna(ocf_pct) else '—'}</b></span>
      </div>
    </div>
    """)


def render_footer():
    """Render the footer with explicit data source attribution and details."""
    st.html("""
    <div style="margin-top: 24px; margin-bottom: 12px; font-family: Tahoma, Arial, sans-serif; font-size: 11px; background: linear-gradient(180deg, #ffffff 0%, #f4f6f9 50%, #e2e7ef 100%); border: 1px solid #9aa6b8; border-radius: 2px; padding: 8px 12px; box-shadow: inset 0 1px 0 #ffffff, 0 1px 2px rgba(0,0,0,0.05); color: #333333;">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
        <div>
          <b>Data Sources:</b>
          &nbsp;&bull;&nbsp;
          <a href="https://stooq.pl" target="_blank" rel="noopener noreferrer" style="color: #1a4a84; font-weight: bold; text-decoration: underline;">Stooq.pl</a>:
          <span style="color: #555555;">Live WSE index constituents (WIG20, mWIG40, sWIG80, WIG) & company directory</span>
          &nbsp;&bull;&nbsp;
          <a href="https://finance.yahoo.com" target="_blank" rel="noopener noreferrer" style="color: #1a4a84; font-weight: bold; text-decoration: underline;">Yahoo Finance (yfinance)</a>:
          <span style="color: #555555;">Quarterly cash flow statements (CapEx, FCF, OCF) & live USD/PLN conversion</span>
        </div>
        <div style="color: #666666; font-size: 10px;">
          WSE HypeScope &bull; Fundamental Research &bull; All financial units in <b>M PLN</b>
        </div>
      </div>
    </div>
    """)
