"""
app.py
------
Sales Dashboard — built with Streamlit + Plotly + SQLite.

Run:
    pip install streamlit plotly pandas
    python generate_data.py   # one-time setup
    streamlit run app.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

import queries

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .main { background-color: #0f1117; }
    .block-container { padding-top: 1.5rem; }

    /* KPI cards */
    .kpi-card {
        background: linear-gradient(135deg, #1e2130 0%, #252836 100%);
        border: 1px solid #2d3148;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        text-align: center;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #4fc3f7;
        margin: 0;
    }
    .kpi-label {
        font-size: 0.78rem;
        color: #8b92a5;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }
    .kpi-delta {
        font-size: 0.82rem;
        color: #66bb6a;
        margin-top: 6px;
    }

    /* Section headings */
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: #c9d1e0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 0.5rem;
        padding-bottom: 6px;
        border-bottom: 2px solid #2d3148;
    }
</style>
""", unsafe_allow_html=True)

# ── Colour palette (consistent across all charts) ─────────────────────────────
ACCENT   = "#4fc3f7"
ACCENT2  = "#f06292"
PALETTE  = ["#4fc3f7", "#f06292", "#66bb6a", "#ffb74d", "#ba68c8", "#4dd0e1"]
BG_CHART = "#1a1d2e"
GRID_COL = "#2d3148"

PLOTLY_LAYOUT = dict(
    paper_bgcolor=BG_CHART,
    plot_bgcolor=BG_CHART,
    font=dict(color="#c9d1e0", family="Segoe UI, sans-serif"),
    margin=dict(l=16, r=16, t=36, b=16),
    xaxis=dict(gridcolor=GRID_COL, zeroline=False),
    yaxis=dict(gridcolor=GRID_COL, zeroline=False),
)


def fmt_currency(value: float) -> str:
    if value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value/1_000:.1f}K"
    return f"${value:,.0f}"


# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/bar-chart.png", width=64)
st.sidebar.title("Sales Dashboard")
st.sidebar.markdown("---")

import sqlite3
conn_raw = sqlite3.connect("sales_data.db")
all_df = pd.read_sql("SELECT * FROM sales", conn_raw)
conn_raw.close()

regions   = ["All"] + sorted(all_df["region"].unique().tolist())
channels  = ["All"] + sorted(all_df["channel"].unique().tolist())
categories = ["All"] + sorted(all_df["category"].unique().tolist())

sel_region   = st.sidebar.selectbox("Region",   regions)
sel_channel  = st.sidebar.selectbox("Channel",  channels)
sel_category = st.sidebar.selectbox("Category", categories)

months = sorted(all_df["sale_date"].str[:7].unique().tolist())
sel_months = st.sidebar.select_slider(
    "Date Range",
    options=months,
    value=(months[0], months[-1]),
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<small style='color:#8b92a5'>Built by ShahulAnalytics · 2024</small>",
    unsafe_allow_html=True,
)

# ── Apply filters ─────────────────────────────────────────────────────────────
df = all_df.copy()
df = df[(df["sale_date"].str[:7] >= sel_months[0]) &
        (df["sale_date"].str[:7] <= sel_months[1])]
if sel_region   != "All": df = df[df["region"]   == sel_region]
if sel_channel  != "All": df = df[df["channel"]  == sel_channel]
if sel_category != "All": df = df[df["category"] == sel_category]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 📊 Sales Analytics Dashboard")
st.markdown(f"<small style='color:#8b92a5'>Showing **{len(df):,}** transactions &nbsp;|&nbsp; {sel_months[0]} → {sel_months[1]}</small>", unsafe_allow_html=True)
st.markdown("---")

# ── KPI Row ───────────────────────────────────────────────────────────────────
total_revenue = df["revenue"].sum()
total_profit  = df["profit"].sum()
total_txns    = len(df)
margin_pct    = (total_profit / total_revenue * 100) if total_revenue else 0
avg_order     = df["revenue"].mean() if len(df) else 0
units_sold    = df["quantity"].sum()

k1, k2, k3, k4, k5, k6 = st.columns(6)
for col, label, value, delta in [
    (k1, "Total Revenue",     fmt_currency(total_revenue), ""),
    (k2, "Total Profit",      fmt_currency(total_profit),  ""),
    (k3, "Profit Margin",     f"{margin_pct:.1f}%",        ""),
    (k4, "Transactions",      f"{total_txns:,}",           ""),
    (k5, "Avg Order Value",   fmt_currency(avg_order),     ""),
    (k6, "Units Sold",        f"{units_sold:,}",           ""),
]:
    col.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-value">{value}</p>
        <p class="kpi-label">{label}</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Revenue Trend + Region Bar ─────────────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown('<p class="section-title">Monthly Revenue & Profit Trend</p>', unsafe_allow_html=True)
    monthly = (
        df.assign(month=df["sale_date"].str[:7])
          .groupby("month")
          .agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
          .reset_index()
          .sort_values("month")
    )
    monthly["month_label"] = pd.to_datetime(monthly["month"]).dt.strftime("%b")

    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    fig_trend.add_trace(go.Bar(
        x=monthly["month_label"], y=monthly["revenue"],
        name="Revenue", marker_color=ACCENT, opacity=0.85,
    ), secondary_y=False)
    fig_trend.add_trace(go.Scatter(
        x=monthly["month_label"], y=monthly["profit"],
        name="Profit", mode="lines+markers",
        line=dict(color=ACCENT2, width=2.5),
        marker=dict(size=6),
    ), secondary_y=True)
    fig_trend.update_layout(**PLOTLY_LAYOUT, legend=dict(
        orientation="h", yanchor="bottom", y=1.02, bgcolor="rgba(0,0,0,0)"
    ))
    fig_trend.update_yaxes(title_text="Revenue ($)", secondary_y=False,
                           gridcolor=GRID_COL, zeroline=False)
    fig_trend.update_yaxes(title_text="Profit ($)", secondary_y=True,
                           gridcolor=GRID_COL, zeroline=False, showgrid=False)
    st.plotly_chart(fig_trend, use_container_width=True)

with col_right:
    st.markdown('<p class="section-title">Revenue by Region</p>', unsafe_allow_html=True)
    reg = (
        df.groupby("region")
          .agg(revenue=("revenue", "sum"))
          .reset_index()
          .sort_values("revenue", ascending=True)
    )
    fig_reg = px.bar(
        reg, x="revenue", y="region", orientation="h",
        color="revenue", color_continuous_scale=["#1e2d4f", ACCENT],
        labels={"revenue": "Revenue ($)", "region": ""},
    )
    fig_reg.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
    fig_reg.update_traces(texttemplate="%{x:$,.0f}", textposition="outside",
                          textfont_size=11)
    st.plotly_chart(fig_reg, use_container_width=True)

# ── Row 2: Top Products + Category Pie ────────────────────────────────────────
col_a, col_b = st.columns([3, 2])

with col_a:
    st.markdown('<p class="section-title">Top 8 Products by Revenue</p>', unsafe_allow_html=True)
    top_prod = (
        df.groupby("product_name")
          .agg(revenue=("revenue", "sum"), profit=("profit", "sum"),
               units=("quantity", "sum"))
          .reset_index()
          .sort_values("revenue", ascending=False)
          .head(8)
    )
    top_prod["margin"] = (top_prod["profit"] / top_prod["revenue"] * 100).round(1)
    fig_prod = px.bar(
        top_prod, x="product_name", y="revenue",
        color="margin", color_continuous_scale=["#1e3a5f", ACCENT],
        labels={"revenue": "Revenue ($)", "product_name": "", "margin": "Margin %"},
        hover_data={"units": True, "margin": True},
    )
    fig_prod.update_layout(**PLOTLY_LAYOUT)
    fig_prod.update_xaxes(tickangle=-30)
    st.plotly_chart(fig_prod, use_container_width=True)

with col_b:
    st.markdown('<p class="section-title">Revenue by Category</p>', unsafe_allow_html=True)
    cat = df.groupby("category")["revenue"].sum().reset_index()
    fig_pie = px.pie(
        cat, names="category", values="revenue",
        color_discrete_sequence=PALETTE, hole=0.45,
    )
    fig_pie.update_layout(
        paper_bgcolor=BG_CHART,
        font=dict(color="#c9d1e0"),
        margin=dict(l=16, r=16, t=16, b=16),
        legend=dict(orientation="v", bgcolor="rgba(0,0,0,0)"),
        showlegend=True,
    )
    fig_pie.update_traces(textinfo="percent+label", textfont_size=12)
    st.plotly_chart(fig_pie, use_container_width=True)

# ── Row 3: Sales Rep Leaderboard + Channel ────────────────────────────────────
col_c, col_d = st.columns([3, 2])

with col_c:
    st.markdown('<p class="section-title">Sales Rep Leaderboard</p>', unsafe_allow_html=True)
    reps = (
        df.groupby("sales_rep")
          .agg(revenue=("revenue", "sum"), profit=("profit", "sum"),
               deals=("sale_id", "count"))
          .reset_index()
          .sort_values("revenue", ascending=False)
    )
    reps["margin"] = (reps["profit"] / reps["revenue"] * 100).round(1)
    reps["revenue_fmt"] = reps["revenue"].apply(fmt_currency)
    reps["profit_fmt"]  = reps["profit"].apply(fmt_currency)
    reps.index = range(1, len(reps) + 1)
    st.dataframe(
        reps[["sales_rep", "revenue_fmt", "profit_fmt", "margin", "deals"]]
            .rename(columns={
                "sales_rep":   "Sales Rep",
                "revenue_fmt": "Revenue",
                "profit_fmt":  "Profit",
                "margin":      "Margin %",
                "deals":       "Deals",
            }),
        use_container_width=True,
        height=260,
    )

with col_d:
    st.markdown('<p class="section-title">Revenue by Channel</p>', unsafe_allow_html=True)
    ch = df.groupby("channel")["revenue"].sum().reset_index().sort_values("revenue", ascending=True)
    fig_ch = px.bar(
        ch, x="revenue", y="channel", orientation="h",
        color="channel", color_discrete_sequence=PALETTE,
        labels={"revenue": "Revenue ($)", "channel": ""},
    )
    fig_ch.update_layout(**PLOTLY_LAYOUT, showlegend=False)
    fig_ch.update_traces(texttemplate="%{x:$,.0f}", textposition="outside")
    st.plotly_chart(fig_ch, use_container_width=True)

# ── Row 4: Raw Data Table ─────────────────────────────────────────────────────
with st.expander("🔍 View Raw Sales Data", expanded=False):
    display_df = df.copy()
    display_df["revenue"] = display_df["revenue"].apply(lambda x: f"${x:,.2f}")
    display_df["profit"]  = display_df["profit"].apply(lambda x: f"${x:,.2f}")
    display_df["discount"] = display_df["discount"].apply(lambda x: f"{x*100:.0f}%")
    st.dataframe(display_df.sort_values("sale_date", ascending=False).head(200),
                 use_container_width=True)

st.markdown("---")
st.markdown(
    "<center><small style='color:#555'>ShahulAnalytics · Sales Dashboard · Python + SQL + Streamlit</small></center>",
    unsafe_allow_html=True,
)
