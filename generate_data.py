"""
generate_data.py
----------------
Generates realistic sample sales data and loads it into a SQLite database.
Run this script first before launching the dashboard.
"""

import sqlite3
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# ── Config ──────────────────────────────────────────────────────────────────
DB_PATH = "sales_data.db"
NUM_RECORDS = 1000
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ── Reference data ───────────────────────────────────────────────────────────
PRODUCTS = {
    "Laptop Pro":      {"category": "Electronics", "base_price": 1200},
    "Wireless Mouse":  {"category": "Accessories",  "base_price":   45},
    "USB-C Hub":       {"category": "Accessories",  "base_price":   80},
    "Monitor 27\"":    {"category": "Electronics", "base_price":  400},
    "Keyboard Mech":   {"category": "Accessories",  "base_price":  130},
    "Webcam HD":       {"category": "Electronics", "base_price":   95},
    "Desk Lamp LED":   {"category": "Office",       "base_price":   60},
    "Standing Desk":   {"category": "Office",       "base_price":  550},
    "Headphones BT":   {"category": "Electronics", "base_price":  180},
    "Notebook Pack":   {"category": "Stationery",   "base_price":   20},
}

REGIONS = ["North", "South", "East", "West", "Central"]
SALES_REPS = [
    "Alice Johnson", "Bob Smith",  "Carol White",
    "David Brown",   "Eva Martinez","Frank Lee",
    "Grace Kim",     "Henry Patel",
]
CHANNELS = ["Online", "In-Store", "Reseller"]


def generate_sales_records(n: int) -> pd.DataFrame:
    start_date = datetime(2024, 1, 1)
    end_date   = datetime(2024, 12, 31)
    date_range = (end_date - start_date).days

    rows = []
    for i in range(1, n + 1):
        product_name = random.choice(list(PRODUCTS.keys()))
        product_info = PRODUCTS[product_name]

        # Simulate seasonality: Q4 gets a 30 % sales boost
        sale_date = start_date + timedelta(days=random.randint(0, date_range))
        season_mult = 1.3 if sale_date.month >= 10 else 1.0

        base_price  = product_info["base_price"]
        quantity    = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 12, 8, 5])[0]
        discount    = round(random.choice([0, 0.05, 0.10, 0.15, 0.20]), 2)
        unit_price  = round(base_price * (1 - discount) * season_mult, 2)
        revenue     = round(unit_price * quantity, 2)
        cost        = round(base_price * quantity * 0.55, 2)
        profit      = round(revenue - cost, 2)

        rows.append({
            "sale_id":      i,
            "sale_date":    sale_date.strftime("%Y-%m-%d"),
            "product_name": product_name,
            "category":     product_info["category"],
            "region":       random.choice(REGIONS),
            "sales_rep":    random.choice(SALES_REPS),
            "channel":      random.choice(CHANNELS),
            "quantity":     quantity,
            "unit_price":   unit_price,
            "discount":     discount,
            "revenue":      revenue,
            "cost":         cost,
            "profit":       profit,
        })

    return pd.DataFrame(rows)


def create_database(df: pd.DataFrame, db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ── Create table ─────────────────────────────────────────────────────────
    cursor.execute("DROP TABLE IF EXISTS sales")
    cursor.execute("""
        CREATE TABLE sales (
            sale_id      INTEGER PRIMARY KEY,
            sale_date    TEXT    NOT NULL,
            product_name TEXT    NOT NULL,
            category     TEXT    NOT NULL,
            region       TEXT    NOT NULL,
            sales_rep    TEXT    NOT NULL,
            channel      TEXT    NOT NULL,
            quantity     INTEGER NOT NULL,
            unit_price   REAL    NOT NULL,
            discount     REAL    NOT NULL,
            revenue      REAL    NOT NULL,
            cost         REAL    NOT NULL,
            profit       REAL    NOT NULL
        )
    """)

    # ── Insert rows ───────────────────────────────────────────────────────────
    df.to_sql("sales", conn, if_exists="replace", index=False)

    # ── Useful views ──────────────────────────────────────────────────────────
    cursor.execute("DROP VIEW IF EXISTS monthly_summary")
    cursor.execute("""
        CREATE VIEW monthly_summary AS
        SELECT
            strftime('%Y-%m', sale_date)  AS month,
            SUM(revenue)                  AS total_revenue,
            SUM(profit)                   AS total_profit,
            COUNT(*)                      AS num_transactions,
            ROUND(AVG(discount) * 100, 1) AS avg_discount_pct
        FROM sales
        GROUP BY month
        ORDER BY month
    """)

    cursor.execute("DROP VIEW IF EXISTS product_summary")
    cursor.execute("""
        CREATE VIEW product_summary AS
        SELECT
            product_name,
            category,
            SUM(quantity)  AS units_sold,
            SUM(revenue)   AS total_revenue,
            SUM(profit)    AS total_profit,
            ROUND(SUM(profit) * 100.0 / SUM(revenue), 1) AS profit_margin_pct
        FROM sales
        GROUP BY product_name, category
        ORDER BY total_revenue DESC
    """)

    cursor.execute("DROP VIEW IF EXISTS region_summary")
    cursor.execute("""
        CREATE VIEW region_summary AS
        SELECT
            region,
            SUM(revenue) AS total_revenue,
            SUM(profit)  AS total_profit,
            COUNT(*)     AS num_transactions
        FROM sales
        GROUP BY region
        ORDER BY total_revenue DESC
    """)

    conn.commit()
    conn.close()
    print(f"✅  Database created at '{db_path}' with {len(df)} records.")


if __name__ == "__main__":
    print("Generating sales data …")
    df = generate_sales_records(NUM_RECORDS)
    create_database(df, DB_PATH)
    print("Done! Run `python app.py` to launch the dashboard.")
