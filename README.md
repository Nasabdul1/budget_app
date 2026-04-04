# 💎 NEXUS Budget Tracker

A professional smart budgeting app built with Python & Streamlit.

## Features
- 📊 **Dashboard** — KPIs, monthly trend chart, category donut chart, budget vs actual
- ➕ **Add Expenses** — Log transactions with category, currency, date & notes
- 📋 **Transactions** — Search, filter, sort, and delete expenses
- 🎯 **Budget Planner** — Set per-category limits with live progress bars & alerts
- 💱 **Currency Converter** — Live exchange rates via Open Exchange Rates API
- ⚙️ **Settings** — Export CSV, clear all data

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

The app opens at http://localhost:8501

## Tech Stack
- **Frontend**: Streamlit + custom CSS
- **Database**: SQLite (auto-created as `nexus_budget.db`)
- **Charts**: Plotly
- **Data**: Pandas
- **Currency**: Open Exchange Rates API (free, no key needed for basic rates)

## Project Structure
```
budget_app/
├── app.py            # Main Streamlit application
├── db.py             # Database init & connection
├── utils.py          # CRUD operations & analytics
├── requirements.txt
└── README.md
```
