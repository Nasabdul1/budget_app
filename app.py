import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
from datetime import datetime, date, timedelta
import calendar
import requests
from db import init_db, get_connection
from utils import (
    add_expense, get_expenses, delete_expense,
    add_budget, get_budgets, get_summary,
    get_category_totals, get_monthly_trend,
    get_spending_alerts, update_expense,
    get_setting, set_setting
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nexus Budget",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="auto"
)

# ── Load icon font & Custom CSS ──────────────────────────────────────────────
st.markdown(
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.31.0/tabler-icons.min.css">',
    unsafe_allow_html=True,
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #111118;
    --surface2: #16161f;
    --border: #1e1e2e;
    --accent: #7c6af7;
    --accent2: #f97316;
    --accent3: #22d3a5;
    --text: #e8e8f0;
    --muted: #6b6b80;
    --danger: #f43f5e;
    --success: #22d3a5;
}

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* Hide default streamlit elements */
#MainMenu, footer {visibility: hidden;}
.stDeployButton {display: none;}
header[data-testid="stHeader"] {
    background: transparent !important;
}

/* Always show sidebar toggle button */
button[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    position: fixed !important;
    top: 0.6rem;
    left: 0.6rem;
    z-index: 1001;
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 0.5rem 0.65rem !important;
    min-width: 2.8rem !important;
    height: 2.8rem !important;
    justify-content: center !important;
    align-items: center !important;
    color: var(--text) !important;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 1.1rem !important;
    font-weight: 600;
}
button[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg {
    display: none !important;
}
button[data-testid="stSidebarCollapsedControl"]::before,
[data-testid="collapsedControl"]::before {
    content: '☰';
    font-size: 1.2rem;
    font-weight: 600;
    display: block;
    line-height: 1;
}
button[data-testid="stSidebarCollapsedControl"]:hover,
[data-testid="collapsedControl"]:hover {
    background: var(--accent) !important;
    transform: scale(1.05);
}

/* Sidebar close button */
section[data-testid="stSidebar"] button[data-testid="stSidebarNavCollapseButton"],
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
    visibility: visible !important;
    display: flex !important;
    color: var(--muted) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .stRadio > label {
    color: var(--muted) !important;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    font-weight: 600;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
}
[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-family: 'DM Mono', monospace !important;
}
[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-size: 1.6rem !important;
    font-weight: 700;
}
[data-testid="stMetricDelta"] svg {display: none;}

/* Buttons */
.stButton > button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #6a5ae0 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(124,106,247,0.35) !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stDateInput > div > div > input,
.stTextArea textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
}
.stSelectbox > div > div:focus-within,
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(124,106,247,0.25) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 7px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: white !important;
}

/* Dataframe */
.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}

/* Alert/info boxes */
.stAlert {
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    background: var(--surface2) !important;
}

/* Plotly chart backgrounds */
.js-plotly-plot {
    border-radius: 12px;
    overflow: hidden;
}

/* Divider */
hr {
    border-color: var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* Labels */
label, .stRadio label span {
    color: var(--muted) !important;
    font-size: 0.8rem !important;
    font-family: 'DM Mono', monospace !important;
    letter-spacing: 0.05em;
}

/* Icon alignment & styling */
.ti {
    vertical-align: -0.125em;
    display: inline-block;
    font-size: inherit;
    line-height: 1;
    font-style: normal;
    font-weight: 400;
    font-feature-settings: "liga";
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
}

/* Icon in buttons and navigation */
button .ti,
a .ti,
span .ti {
    vertical-align: middle;
    margin: 0;
    padding: 0;
}

/* ── Mobile Responsive ───────────────────────────────────── */
@media (max-width: 768px) {
    /* Stack columns vertically */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }

    /* Mobile sidebar remains hidden */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    button[data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Add bottom padding to avoid content being hidden under fixed nav */
    .stMainBlockContainer, .block-container {
        padding-bottom: 6rem !important;
    }
    
    /* Smaller metric cards */
    [data-testid="metric-container"] {
        padding: 0.7rem 0.8rem;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
    }

    /* Compact page header */
    h1 {
        font-size: 1.5rem !important;
    }

    /* Keep content visible above fixed nav */
    .main [data-testid="stVerticalBlock"] {
        margin-bottom: 5.6rem !important;
    }

    /* Plotly charts fit viewport */
    .js-plotly-plot {
        width: 100% !important;
    }

    /* Smaller button padding */
    .stButton > button {
        padding: 0.45rem 0.8rem !important;
        font-size: 0.8rem !important;
    }

    /* Main content padding */
    .stMainBlockContainer, .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
}

@media (max-width: 480px) {
    [data-testid="stMetricValue"] {
        font-size: 1rem !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.62rem !important;
    }
    h1 {
        font-size: 1.3rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ── Init DB ───────────────────────────────────────────────────────────────────
init_db()

# ── Helpers ───────────────────────────────────────────────────────────────────
CATEGORIES = [
    "Food & Dining", "Housing & Rent", "Transport",
    "Health & Wellness", "Entertainment", "Shopping",
    "Education", "Travel", "Utilities", "Business",
    "Gifts & Donations", "Subscriptions", "Fitness", "Pets", "Other"
]

CATEGORY_ICONS = {
    "Food & Dining": "ti-tools-kitchen-2",
    "Housing & Rent": "ti-home-2",
    "Transport": "ti-car",
    "Health & Wellness": "ti-heart-rate-monitor",
    "Entertainment": "ti-device-gamepad-2",
    "Shopping": "ti-shopping-bag",
    "Education": "ti-book",
    "Travel": "ti-plane",
    "Utilities": "ti-bulb",
    "Business": "ti-briefcase",
    "Gifts & Donations": "ti-gift",
    "Subscriptions": "ti-device-mobile",
    "Fitness": "ti-barbell",
    "Pets": "ti-paw",
    "Other": "ti-tool",
}

CURRENCIES = ["USD", "EUR", "GBP", "NGN", "CAD", "AUD", "JPY", "INR", "GHS", "KES"]

CHART_TEMPLATE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Syne", color="#6b6b80", size=11),
    margin=dict(t=30, b=20, l=10, r=10),
    colorway=["#7c6af7","#f97316","#22d3a5","#f43f5e","#38bdf8","#facc15","#c084fc","#fb7185","#4ade80","#60a5fa"]
)

def fmt_currency(val, cur="USD"):
    symbols = {"USD":"$","EUR":"€","GBP":"£","NGN":"₦","CAD":"CA$","AUD":"A$","JPY":"¥","INR":"₹","GHS":"₵","KES":"KSh"}
    sym = symbols.get(cur, cur + " ")
    return f"{sym}{val:,.2f}"


def cat_icon(category, size="1rem", color="#7c6af7"):
    ic = CATEGORY_ICONS.get(category, "ti-tool")
    return f'<span style="display:inline-flex;align-items:center;justify-content:center;height:{size};width:{size};"><i class="ti {ic}" style="font-size:{size};color:{color};line-height:1;"></i></span>'


# ── Load base currency ────────────────────────────────────────────────────────
if "base_currency" not in st.session_state:
    st.session_state.base_currency = get_setting("base_currency", "USD")

# ── Navigation state ───────────────────────────────────────────────────────────
page_options = [
    "Dashboard",
    "Add Expense",
    "Transactions",
    "Budgets",
    "Currency",
    "Settings"
]

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0 1.5rem;">
        <div style="font-size:1.6rem; font-weight:800; letter-spacing:-0.02em; color:#e8e8f0;">
            NEXUS<span style="color:#7c6af7;">.</span>
        </div>
        <div style="font-size:0.7rem; color:#6b6b80; letter-spacing:0.15em; text-transform:uppercase; margin-top:2px; font-family:'DM Mono',monospace;">
            Smart Budget Tracker
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("Navigation", page_options, index=page_options.index(st.session_state.page), key="sidebar_page", label_visibility="visible")

    st.markdown("---")

    # Quick currency selector – defaults to saved base currency
    base_idx = CURRENCIES.index(st.session_state.base_currency) if st.session_state.base_currency in CURRENCIES else 0
    currency = st.selectbox("Display Currency", CURRENCIES, index=base_idx, key="currency")

    # Date range filter
    st.markdown("<div style='font-size:0.7rem;color:#6b6b80;letter-spacing:0.1em;text-transform:uppercase;font-family:DM Mono,monospace;margin-bottom:4px;'>Date Range</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", value=date.today().replace(day=1), label_visibility="collapsed")
    with col2:
        end_date = st.date_input("To", value=date.today(), label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f"<div style='font-size:0.68rem;color:#3a3a50;text-align:center;font-family:DM Mono,monospace;'>{datetime.now().strftime('%A, %d %b %Y')}</div>", unsafe_allow_html=True)

st.session_state.page = st.session_state.sidebar_page
page = st.session_state.page

# ── Mobile bottom navigation (desktop hidden) ──────────────────────────────────
nav_items = [
    ("Dashboard", "ti-layout-dashboard"),
    ("Add Expense", "ti-plus"),
    ("Transactions", "ti-list-details"),
    ("Budgets", "ti-wallet"),
    ("Currency", "ti-currency-dollar"),
    ("Settings", "ti-settings")
]

nav_html = """
<style>
.mobile-nav-container {
    display: none;
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: var(--surface);
    border-top: 1px solid var(--border);
    z-index: 1002;
    padding: 0;
    margin: 0;
}

@media (max-width: 768px) {
    .mobile-nav-container {
        display: flex;
    }
    
    .nav-button {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 0.5rem 0.25rem;
        gap: 0.3rem;
        color: var(--muted);
        font-size: 0.65rem;
        font-family: 'Syne', sans-serif;
        font-weight: 600;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.2s ease;
        border: none;
        background: transparent;
    }
    
    .nav-button:hover,
    .nav-button.active {
        color: var(--text);
    }
    
    .nav-button.active i {
        color: var(--accent);
        font-size: 1.35rem;
    }
    
    .nav-button i {
        font-size: 1.2rem;
        transition: all 0.2s ease;
    }
}
</style>
"""
st.markdown(nav_html, unsafe_allow_html=True)

# ── Mobile Navigation Buttons ────────────────────────────────────────────────────
# Create columns for mobile navigation (will be styled by CSS above)
st.markdown("""
<div style='position: fixed; bottom: 0; left: 0; width: 100%; background: var(--surface); border-top: 1px solid var(--border); padding: 0.65rem 0.35rem; z-index: 1002; display: none;' class='mobile-nav-container' id='mobile-nav'>
</div>
""", unsafe_allow_html=True)

# Store navigation items for reference
if "nav_items" not in st.session_state:
    st.session_state.nav_items = nav_items


# ── Helper: alerts banner ─────────────────────────────────────────────────────
def show_alerts():
    alerts = get_spending_alerts(start_date, end_date)
    if alerts:
        for a in alerts:
            st.markdown(f"""
            <div style="background:rgba(244,63,94,0.1);border:1px solid rgba(244,63,94,0.3);
                        border-radius:10px;padding:0.65rem 1rem;margin-bottom:0.5rem;display:flex;align-items:center;gap:0.7rem;">
                <i class="ti ti-alert-triangle" style="font-size:1.1rem;color:#f43f5e;"></i>
                <span style="font-size:0.82rem;color:#f43f5e;font-weight:600;">{a}</span>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown("<h1 style='font-size:2rem;font-weight:800;letter-spacing:-0.03em;margin-bottom:0.2rem;'>Financial Overview</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#6b6b80;font-size:0.85rem;font-family:DM Mono,monospace;margin-bottom:1.5rem;'>{start_date.strftime('%b %d')} → {end_date.strftime('%b %d, %Y')}</p>", unsafe_allow_html=True)

    show_alerts()

    summary = get_summary(start_date, end_date)
    cat_totals = get_category_totals(start_date, end_date)
    monthly = get_monthly_trend()

    # ── KPI Row ───────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    total_spent = summary.get("total", 0)
    tx_count = summary.get("count", 0)
    avg_tx = total_spent / tx_count if tx_count else 0
    budgets = get_budgets()
    total_budget = sum(b["amount"] for b in budgets)
    remaining = total_budget - total_spent if total_budget else 0

    with k1:
        st.metric("Total Spent", fmt_currency(total_spent, currency))
    with k2:
        st.metric("Transactions", f"{tx_count}")
    with k3:
        st.metric("Avg. per Transaction", fmt_currency(avg_tx, currency))
    with k4:
        st.metric("Budget Remaining", fmt_currency(abs(remaining), currency),
                  delta="over budget" if remaining < 0 else "within budget",
                  delta_color="inverse" if remaining < 0 else "normal")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row ────────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        if not monthly.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=monthly["month"], y=monthly["total"],
                marker=dict(
                    color=monthly["total"],
                    colorscale=[[0,"#1e1e2e"],[0.5,"#4a3fa0"],[1,"#7c6af7"]],
                    line=dict(width=0)
                ),
                text=[fmt_currency(v, currency) for v in monthly["total"]],
                textposition="outside",
                textfont=dict(size=10, family="DM Mono"),
                hovertemplate="<b>%{x}</b><br>Spent: %{y:,.2f}<extra></extra>"
            ))
            fig.update_layout(**CHART_TEMPLATE, height=260,
                              xaxis=dict(showgrid=False, tickfont=dict(size=10)),
                              yaxis=dict(showgrid=True, gridcolor="#1e1e2e", tickfont=dict(size=10)),
                              title=dict(text="Monthly Spending Trend", font=dict(size=13, color="#e8e8f0"), x=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data yet — add some expenses to see trends.")

    with col_right:
        if not cat_totals.empty:
            fig2 = go.Figure(go.Pie(
                labels=cat_totals["category"],
                values=cat_totals["total"],
                hole=0.65,
                textinfo="none",
                hovertemplate="<b>%{label}</b><br>%{value:,.2f} (%{percent})<extra></extra>",
                marker=dict(colors=CHART_TEMPLATE["colorway"], line=dict(color="#0a0a0f", width=2))
            ))
            fig2.update_layout(**CHART_TEMPLATE, height=260,
                               showlegend=True,
                               legend=dict(orientation="v", font=dict(size=10), x=1.0, y=0.5),
                               title=dict(text="By Category", font=dict(size=13, color="#e8e8f0"), x=0),
                               annotations=[dict(text=f"<b>{tx_count}</b><br>txns", x=0.5, y=0.5,
                                                 font=dict(size=13, color="#e8e8f0"), showarrow=False)])
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No category data yet.")

    # ── Budget vs Actual ──────────────────────────────────────────────────────
    if budgets and not cat_totals.empty:
        st.markdown("### Budget vs Actual")
        bdf = pd.DataFrame(budgets)
        cdf = cat_totals.copy()
        merged = bdf.merge(cdf, on="category", how="left").fillna(0)
        merged["pct"] = (merged["total"] / merged["amount"] * 100).clip(0, 150)

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(name="Budget", x=merged["category"], y=merged["amount"],
                               marker_color="#1e1e2e", marker_line_width=0))
        fig3.add_trace(go.Bar(name="Spent", x=merged["category"], y=merged["total"],
                               marker=dict(color=["#f43f5e" if p > 100 else "#7c6af7" for p in merged["pct"]]),
                               marker_line_width=0))
        fig3.update_layout(**CHART_TEMPLATE, height=260, barmode="overlay",
                           legend=dict(orientation="h", x=0, y=1.1),
                           xaxis=dict(showgrid=False, tickfont=dict(size=10)),
                           yaxis=dict(showgrid=True, gridcolor="#1e1e2e"))
        st.plotly_chart(fig3, use_container_width=True)

    # ── Recent transactions ───────────────────────────────────────────────────
    st.markdown("### Recent Transactions")
    expenses = get_expenses(start_date, end_date, limit=8)
    if expenses:
        for e in expenses:
            amt_color = "#f43f5e" if e["amount"] > 500 else "#7c6af7"
            ic = cat_icon(e["category"])
            st.markdown(f"""
            <div style="background:var(--surface2);border:1px solid var(--border);border-radius:10px;
                        padding:0.75rem 1rem;margin-bottom:0.4rem;display:flex;justify-content:space-between;align-items:center;">
                <div style="display:flex;align-items:center;gap:1rem;">
                    <div style="width:36px;height:36px;background:rgba(124,106,247,0.15);border-radius:8px;
                                display:flex;align-items:center;justify-content:center;">
                        {ic}
                    </div>
                    <div>
                        <div style="font-weight:600;font-size:0.88rem;">{e['description']}</div>
                        <div style="font-size:0.72rem;color:#6b6b80;font-family:DM Mono,monospace;">{e['category']} · {e['date']}</div>
                    </div>
                </div>
                <div style="font-family:DM Mono,monospace;font-weight:700;color:{amt_color};">
                    {fmt_currency(e['amount'], currency)}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No transactions in this date range.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ADD EXPENSE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Add Expense":
    st.markdown("<h1 style='font-size:2rem;font-weight:800;letter-spacing:-0.03em;'>Add Expense</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6b6b80;font-size:0.85rem;font-family:DM Mono,monospace;margin-bottom:1.5rem;'>Record a new transaction</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.5, 1])
    with col1:
        with st.container():
            st.markdown("<div style='background:var(--surface2);border:1px solid var(--border);border-radius:14px;padding:1.5rem;'>", unsafe_allow_html=True)

            desc = st.text_input("Description", placeholder="e.g. Groceries at Shoprite")
            a1, a2 = st.columns(2)
            with a1:
                amount = st.number_input("Amount", min_value=0.01, value=10.00, step=0.01, format="%.2f")
            with a2:
                exp_currency = st.selectbox("Currency", CURRENCIES, key="exp_cur")

            cat = st.selectbox("Category", CATEGORIES)
            exp_date = st.date_input("Date", value=date.today())
            notes = st.text_area("Notes (optional)", placeholder="Any additional details...", height=80)

            if st.button("Save Expense", use_container_width=True):
                if desc:
                    add_expense(desc, amount, exp_currency, cat, str(exp_date), notes)
                    st.success("Expense saved successfully!")
                else:
                    st.error("Please enter a description.")

            st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(124,106,247,0.15),rgba(34,211,165,0.08));
                    border:1px solid rgba(124,106,247,0.2);border-radius:14px;padding:1.5rem;">
            <div style="font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase;
                        color:#7c6af7;font-family:DM Mono,monospace;margin-bottom:1rem;">Quick Tips</div>
        """, unsafe_allow_html=True)

        tips = [
            ("ti-target", "Be specific", "Clear descriptions help you track patterns better."),
            ("ti-calendar", "Log daily", "Daily logging prevents forgotten expenses."),
            ("ti-tag", "Categorize", "Consistent categories enable better insights."),
            ("ti-note", "Use notes", "Notes help remember context later."),
        ]
        for icon_cls, title, text in tips:
            st.markdown(f"""
            <div style="margin-bottom:0.8rem;">
                <div style="font-weight:700;font-size:0.82rem;">
                    <i class="ti {icon_cls}" style="color:#7c6af7;margin-right:0.4rem;"></i>{title}
                </div>
                <div style="font-size:0.75rem;color:#6b6b80;">{text}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: TRANSACTIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Transactions":
    st.markdown("<h1 style='font-size:2rem;font-weight:800;letter-spacing:-0.03em;'>Transactions</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6b6b80;font-size:0.85rem;font-family:DM Mono,monospace;margin-bottom:1.5rem;'>All recorded expenses</p>", unsafe_allow_html=True)

    f1, f2, f3 = st.columns([1.5, 1, 1])
    with f1:
        search = st.text_input("Search", placeholder="Search transactions...")
    with f2:
        cat_filter = st.selectbox("Category", ["All"] + CATEGORIES)
    with f3:
        sort_by = st.selectbox("Sort by", ["Date (newest)", "Date (oldest)", "Amount (high)", "Amount (low)"])

    expenses = get_expenses(start_date, end_date)
    if expenses:
        df = pd.DataFrame(expenses)
        if search:
            df = df[df["description"].str.contains(search, case=False, na=False)]
        if cat_filter != "All":
            df = df[df["category"] == cat_filter]

        sort_map = {
            "Date (newest)": ("date", False),
            "Date (oldest)": ("date", True),
            "Amount (high)": ("amount", False),
            "Amount (low)": ("amount", True),
        }
        col_s, asc_s = sort_map[sort_by]
        df = df.sort_values(col_s, ascending=asc_s)

        st.markdown(f"<div style='font-size:0.75rem;color:#6b6b80;font-family:DM Mono,monospace;margin-bottom:0.8rem;'>{len(df)} transactions · Total: {fmt_currency(df['amount'].sum(), currency)}</div>", unsafe_allow_html=True)

        for _, row in df.iterrows():
            with st.expander(f"{row['description']}  —  {fmt_currency(row['amount'], currency)}  ·  {row['date']}"):
                edit_mode = st.session_state.get(f"editing_{row['id']}", False)

                if not edit_mode:
                    # ── View mode ──
                    ec1, ec2, ec3 = st.columns([2.5, 1.5, 1])
                    with ec1:
                        st.markdown(f"**Category:** {row['category']}")
                        st.markdown(f"**Notes:** {row['notes'] or '—'}")
                    with ec2:
                        st.markdown(f"**Currency:** {row['currency']}")
                        st.markdown(f"**Date:** {row['date']}")
                    with ec3:
                        if st.button("Edit", key=f"btn_edit_{row['id']}"):
                            st.session_state[f"editing_{row['id']}"] = True
                            st.rerun()
                        if st.button("Delete", key=f"btn_del_{row['id']}"):
                            delete_expense(row["id"])
                            st.rerun()
                else:
                    # ── Edit mode ──
                    with st.form(f"form_edit_{row['id']}"):
                        new_desc = st.text_input("Description", value=row["description"], key=f"ed_desc_{row['id']}")
                        fc1, fc2 = st.columns(2)
                        with fc1:
                            new_amount = st.number_input(
                                "Amount", value=float(row["amount"]),
                                min_value=0.01, step=0.01, format="%.2f",
                                key=f"ed_amt_{row['id']}"
                            )
                        with fc2:
                            cur_idx = CURRENCIES.index(row["currency"]) if row["currency"] in CURRENCIES else 0
                            new_cur = st.selectbox("Currency", CURRENCIES, index=cur_idx, key=f"ed_cur_{row['id']}")
                        cat_idx = CATEGORIES.index(row["category"]) if row["category"] in CATEGORIES else len(CATEGORIES) - 1
                        new_cat = st.selectbox("Category", CATEGORIES, index=cat_idx, key=f"ed_cat_{row['id']}")
                        new_date = st.date_input("Date", value=datetime.strptime(row["date"], "%Y-%m-%d").date(), key=f"ed_date_{row['id']}")
                        new_notes = st.text_area("Notes", value=row["notes"] or "", key=f"ed_notes_{row['id']}")

                        if st.form_submit_button("Save Changes", use_container_width=True):
                            update_expense(
                                row["id"],
                                description=new_desc, amount=new_amount,
                                currency=new_cur, category=new_cat,
                                date=str(new_date), notes=new_notes
                            )
                            st.session_state[f"editing_{row['id']}"] = False
                            st.rerun()

                    if st.button("Cancel", key=f"btn_cancel_{row['id']}"):
                        st.session_state[f"editing_{row['id']}"] = False
                        st.rerun()
    else:
        st.info("No transactions found for the selected range.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: BUDGETS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Budgets":
    st.markdown("<h1 style='font-size:2rem;font-weight:800;letter-spacing:-0.03em;'>Budget Planner</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6b6b80;font-size:0.85rem;font-family:DM Mono,monospace;margin-bottom:1.5rem;'>Set spending limits per category</p>", unsafe_allow_html=True)

    ba, bb = st.columns([1, 1.5])

    with ba:
        st.markdown("<div style='background:var(--surface2);border:1px solid var(--border);border-radius:14px;padding:1.5rem;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase;color:#7c6af7;font-family:DM Mono,monospace;margin-bottom:1rem;'>Set Budget</div>", unsafe_allow_html=True)

        b_cat = st.selectbox("Category", CATEGORIES, key="budget_cat")
        b_amt = st.number_input("Monthly Limit", min_value=1.0, value=500.0, step=10.0, format="%.2f")
        b_cur = st.selectbox("Currency", CURRENCIES, key="budget_cur")

        if st.button("Save Budget", use_container_width=True):
            add_budget(b_cat, b_amt, b_cur)
            st.success("Budget saved!")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with bb:
        budgets = get_budgets()
        cat_totals = get_category_totals(start_date, end_date)

        if budgets:
            bdf = pd.DataFrame(budgets)
            for _, b in bdf.iterrows():
                spent_row = cat_totals[cat_totals["category"] == b["category"]] if not cat_totals.empty else pd.DataFrame()
                spent = spent_row["total"].values[0] if not spent_row.empty else 0
                pct = min(spent / b["amount"] * 100, 100) if b["amount"] > 0 else 0
                over = spent > b["amount"]
                bar_color = "#f43f5e" if over else "#7c6af7"
                status_text = "Over budget!" if over else f"{100-pct:.0f}% remaining"
                ic = cat_icon(b["category"], size="0.9rem")

                st.markdown(f"""
                <div style="background:var(--surface2);border:1px solid var(--border);border-radius:12px;
                            padding:1rem 1.2rem;margin-bottom:0.6rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                        <div style="font-weight:700;font-size:0.85rem;">{ic} {b['category']}</div>
                        <div style="font-family:DM Mono,monospace;font-size:0.8rem;color:{'#f43f5e' if over else '#6b6b80'};">
                            {fmt_currency(spent, currency)} / {fmt_currency(b['amount'], currency)}
                        </div>
                    </div>
                    <div style="background:#1e1e2e;border-radius:99px;height:6px;overflow:hidden;">
                        <div style="width:{pct}%;background:{bar_color};height:100%;border-radius:99px;
                                    transition:width 0.5s ease;"></div>
                    </div>
                    <div style="font-size:0.7rem;color:#6b6b80;margin-top:0.35rem;font-family:DM Mono,monospace;">
                        {status_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No budgets set yet.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CURRENCY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Currency":
    st.markdown("<h1 style='font-size:2rem;font-weight:800;letter-spacing:-0.03em;'>Currency Converter</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6b6b80;font-size:0.85rem;font-family:DM Mono,monospace;margin-bottom:1.5rem;'>Live exchange rates</p>", unsafe_allow_html=True)

    @st.cache_data(ttl=3600)
    def get_rates(base="USD"):
        try:
            r = requests.get(f"https://open.er-api.com/v6/latest/{base}", timeout=5)
            if r.status_code == 200:
                return r.json().get("rates", {})
        except Exception:
            pass
        return {}

    c1, c2, c3 = st.columns([1, 0.3, 1])
    with c1:
        from_cur = st.selectbox("From", CURRENCIES, key="from_cur")
        amount_c = st.number_input("Amount", min_value=0.0, value=100.0, step=1.0)
    with c2:
        st.markdown('<div style="text-align:center;padding-top:2.5rem;font-size:1.5rem;"><i class="ti ti-arrows-exchange" style="color:#7c6af7;"></i></div>', unsafe_allow_html=True)
    with c3:
        to_cur = st.selectbox("To", CURRENCIES, index=1, key="to_cur")

    if st.button("Convert"):
        rates = get_rates(from_cur)
        if rates and to_cur in rates:
            converted = amount_c * rates[to_cur]
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(124,106,247,0.15),rgba(34,211,165,0.08));
                        border:1px solid rgba(124,106,247,0.3);border-radius:14px;padding:2rem;text-align:center;margin-top:1rem;">
                <div style="font-size:0.75rem;color:#6b6b80;font-family:DM Mono,monospace;margin-bottom:0.5rem;">{amount_c:,.2f} {from_cur} =</div>
                <div style="font-size:2.5rem;font-weight:800;color:#7c6af7;">{converted:,.4f} {to_cur}</div>
                <div style="font-size:0.72rem;color:#6b6b80;font-family:DM Mono,monospace;margin-top:0.5rem;">1 {from_cur} = {rates[to_cur]:.4f} {to_cur}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("Could not fetch exchange rates. Check your internet connection.")

    # Rate table
    st.markdown("### Live Rates vs USD")
    rates_usd = get_rates("USD")
    if rates_usd:
        rate_data = [{"Currency": c, "Rate (vs USD)": f"{rates_usd.get(c, 'N/A'):,.4f}" if c in rates_usd else "N/A"} for c in CURRENCIES]
        st.dataframe(pd.DataFrame(rate_data), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Settings":
    st.markdown("<h1 style='font-size:2rem;font-weight:800;letter-spacing:-0.03em;'>Settings</h1>", unsafe_allow_html=True)

    st.markdown("### Base Currency")
    st.markdown("<p style='color:#6b6b80;font-size:0.82rem;margin-bottom:0.8rem;'>Set the default currency used across the app.</p>", unsafe_allow_html=True)
    cur_idx = CURRENCIES.index(st.session_state.base_currency) if st.session_state.base_currency in CURRENCIES else 0
    new_base = st.selectbox("Default Currency", CURRENCIES, index=cur_idx, key="base_cur_setting")
    if st.button("Save Base Currency"):
        set_setting("base_currency", new_base)
        st.session_state.base_currency = new_base
        st.success(f"Base currency updated to {new_base}.")
        st.rerun()

    st.markdown("---")

    st.markdown("### Export Data")
    expenses = get_expenses(date(2000,1,1), date(2099,1,1))
    if expenses:
        df_export = pd.DataFrame(expenses)
        csv = df_export.to_csv(index=False)
        st.download_button("Download CSV", data=csv, file_name="nexus_expenses.csv", mime="text/csv")
    else:
        st.info("No data to export yet.")

    st.markdown("---")
    st.markdown("### Danger Zone")
    with st.expander("Clear all data"):
        st.warning("This will permanently delete ALL expenses and budgets.")
        confirm = st.text_input("Type DELETE to confirm")
        if st.button("Clear All Data") and confirm == "DELETE":
            conn = get_connection()
            conn.execute("DELETE FROM expenses")
            conn.execute("DELETE FROM budgets")
            conn.commit()
            conn.close()
            st.success("All data cleared.")
            st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center;padding:2rem;color:#3a3a50;font-size:0.72rem;font-family:DM Mono,monospace;">
        NEXUS Budget Tracker · Built with Streamlit · v1.1.0
    </div>
    """, unsafe_allow_html=True)
