"""
queries.py
----------
All SQL queries used by the dashboard, kept in one place for easy maintenance.
"""

import sqlite3
import pandas as pd

DB_PATH = "sales_data.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


# ── KPI Cards ────────────────────────────────────────────────────────────────

def get_kpi_summary() -> dict:
    sql = """
        SELECT
            ROUND(SUM(revenue), 2)                              AS total_revenue,
            ROUND(SUM(profit), 2)                               AS total_profit,
            COUNT(*)                                            AS total_transactions,
            ROUND(SUM(profit) * 100.0 / SUM(revenue), 1)       AS profit_margin_pct,
            ROUND(AVG(revenue), 2)                              AS avg_order_value,
            SUM(quantity)                                       AS total_units_sold
        FROM sales
    """
    with get_connection() as conn:
        row = pd.read_sql(sql, conn).iloc[0]
    return row.to_dict()


# ── Monthly Trend ────────────────────────────────────────────────────────────

def get_monthly_trend() -> pd.DataFrame:
    sql = """
        SELECT
            strftime('%b %Y', sale_date) AS month_label,
            strftime('%Y-%m', sale_date) AS month_sort,
            ROUND(SUM(revenue), 2)       AS revenue,
            ROUND(SUM(profit), 2)        AS profit,
            COUNT(*)                     AS transactions
        FROM sales
        GROUP BY month_sort
        ORDER BY month_sort
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn)


# ── Revenue by Region ─────────────────────────────────────────────────────────

def get_region_revenue() -> pd.DataFrame:
    sql = """
        SELECT
            region,
            ROUND(SUM(revenue), 2) AS revenue,
            ROUND(SUM(profit), 2)  AS profit,
            COUNT(*)               AS transactions
        FROM sales
        GROUP BY region
        ORDER BY revenue DESC
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn)


# ── Top Products ──────────────────────────────────────────────────────────────

def get_top_products(limit: int = 10) -> pd.DataFrame:
    sql = f"""
        SELECT
            product_name,
            category,
            SUM(quantity)  AS units_sold,
            ROUND(SUM(revenue), 2) AS revenue,
            ROUND(SUM(profit), 2)  AS profit,
            ROUND(SUM(profit) * 100.0 / SUM(revenue), 1) AS margin_pct
        FROM sales
        GROUP BY product_name
        ORDER BY revenue DESC
        LIMIT {limit}
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn)


# ── Sales by Channel ──────────────────────────────────────────────────────────

def get_channel_breakdown() -> pd.DataFrame:
    sql = """
        SELECT
            channel,
            ROUND(SUM(revenue), 2) AS revenue,
            COUNT(*) AS transactions
        FROM sales
        GROUP BY channel
        ORDER BY revenue DESC
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn)


# ── Sales Rep Leaderboard ─────────────────────────────────────────────────────

def get_rep_leaderboard() -> pd.DataFrame:
    sql = """
        SELECT
            sales_rep,
            ROUND(SUM(revenue), 2) AS revenue,
            ROUND(SUM(profit), 2)  AS profit,
            COUNT(*)               AS deals,
            ROUND(AVG(revenue), 2) AS avg_deal_size
        FROM sales
        GROUP BY sales_rep
        ORDER BY revenue DESC
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn)


# ── Category Mix ──────────────────────────────────────────────────────────────

def get_category_mix() -> pd.DataFrame:
    sql = """
        SELECT
            category,
            ROUND(SUM(revenue), 2) AS revenue,
            SUM(quantity)          AS units_sold
        FROM sales
        GROUP BY category
        ORDER BY revenue DESC
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn)
