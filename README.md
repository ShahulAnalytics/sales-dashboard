# 📊 Sales Analytics Dashboard

> **Transforming raw sales data into actionable insights** — built with Python, SQL, and Streamlit.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-SQLite-003B57?style=flat&logo=sqlite&logoColor=white)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Charts-Plotly-3F4F75?style=flat&logo=plotly&logoColor=white)

---

## 🚀 Overview

An end-to-end **sales analytics dashboard** that covers the full data pipeline:

1. **Data Generation** — Realistic 1,000-record sales dataset with seasonality
2. **SQL Layer** — SQLite database with optimised views for fast querying
3. **Interactive Dashboard** — Streamlit + Plotly with live filters

---

## ✨ Features

| Feature | Description |
|---|---|
| 📈 Revenue Trend | Monthly revenue & profit with dual-axis chart |
| 🗺️ Region Analysis | Revenue breakdown across 5 regions |
| 🏆 Product Ranking | Top products by revenue with margin colour-coding |
| 🧩 Category Mix | Donut chart for category revenue split |
| 👤 Rep Leaderboard | Ranked sales rep performance table |
| 📡 Channel Split | Online vs In-Store vs Reseller comparison |
| 🔍 Raw Data Explorer | Filterable table of all transactions |
| 🎛️ Live Filters | Region, Channel, Category, Date Range |

---

## 🛠️ Tech Stack

- **Python 3.10+** — core language
- **SQLite + SQL** — data storage and aggregation views
- **Pandas** — data manipulation
- **Streamlit** — dashboard framework
- **Plotly** — interactive charts

---

## ⚡ Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/ShahulAnalytics/sales-dashboard.git
cd sales-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate the database (run once)
python generate_data.py

# 4. Launch the dashboard
streamlit run app.py
```

Open your browser at **http://localhost:8501** 🎉

---

## 📁 Project Structure

```
sales-dashboard/
├── generate_data.py   # Generates sample data → SQLite DB
├── queries.py         # All SQL queries (reusable module)
├── app.py             # Streamlit dashboard
├── requirements.txt   # Python dependencies
└── README.md
```

---

## 📸 Dashboard Preview

The dashboard includes:
- **6 KPI cards** — Revenue, Profit, Margin, Transactions, AOV, Units
- **6 interactive charts** — trends, bars, pie, leaderboard
- **Sidebar filters** — slice data by region, channel, category, and date
- **Dark theme** — professional analytics aesthetic

---

## 🧠 SQL Highlights

The project uses SQLite **views** for clean, reusable aggregations:

```sql
-- Monthly performance view
CREATE VIEW monthly_summary AS
SELECT
    strftime('%Y-%m', sale_date)          AS month,
    ROUND(SUM(revenue), 2)                AS total_revenue,
    ROUND(SUM(profit), 2)                 AS total_profit,
    COUNT(*)                              AS num_transactions,
    ROUND(AVG(discount) * 100, 1)         AS avg_discount_pct
FROM sales
GROUP BY month
ORDER BY month;
```

---

## 👤 Author

**Shahul M** — Data Analyst  
📧 shahul.analytics@gmail.com  
🔗 [github.com/ShahulAnalytics](https://github.com/ShahulAnalytics)

---

*Built to demonstrate end-to-end analytics: data generation → SQL → Python → interactive dashboard.*
