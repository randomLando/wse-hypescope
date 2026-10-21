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
    """Render the Windows 7 / Stooq-style glossy header banner."""
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
    </style>
    <div style="font-family: Tahoma, Arial, sans-serif; font-size: 12px; color: #000; margin-bottom: 6px;">
      <div style="display: flex; align-items: baseline; justify-content: space-between; padding: 6px 2px;">
        <span style="font-family: Arial, Helvetica, sans-serif; font-size: 28px; font-weight: bold; letter-spacing: -0.5px; color: #000;">WSE HypeScope</span>
        <span style="font-size: 12px; color: #222;">Live <b>USD/PLN</b>: <span style="background: linear-gradient(180deg, #e8f8ec 0%, #c8ebd0 100%); border: 1px solid #8ec99c; color: #006600; font-weight: bold; padding: 1px 6px;">{usd_pln:.4f}</span> &nbsp;|&nbsp; Unit: <b>M PLN</b></span>
      </div>
      <div style="background: linear-gradient(180deg, #7b8da6 0%, #5d6e87 48%, #4a5b75 52%, #3f4f66 100%); color: #ffffff; padding: 6px 10px; font-weight: bold; text-shadow: 0 -1px 0 rgba(0,0,0,0.4); border-top: 1px solid #9ab0cc; border-bottom: 1px solid #2d394b;">
        WSE Fundamental Research: Capital Expenditure (CapEx) vs. Free Cash Flow (FCF)
      </div>
    </div>
    """)


def render_section_header(title, variant="blue"):
    """Render a glossy Windows 7 / Stooq section header bar ('blue' or 'silver')."""
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
      <div style="border-bottom:1px solid #cfd6e0; padding-bottom:3px; margin-bottom:5px;">
        <b>Latest Quarter Summary ({df.index[0]}):</b>
        <span style="color:{status_color}; font-weight:bold; margin-left:6px;">{status_label}</span>
      </div>
      <div style="display:flex; justify-content:space-between;">
        <span>CapEx: <b>{f'{capex_val:,.2f}' if pd.notna(capex_val) else '—'} M PLN</b></span>
        <span>Free Cash Flow (FCF): <b style="color:{status_color};">{f'{fcf_val:+,.2f}' if pd.notna(fcf_val) else '—'} M PLN</b></span>
        <span>CapEx / OCF: <b>{f'{ocf_pct:.2f}%' if pd.notna(ocf_pct) else '—'}</b></span>
      </div>
    </div>
    """)
