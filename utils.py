import pandas as pd
from datetime import date, timedelta
from db import get_connection


# ── Settings ──────────────────────────────────────────────────────────────────

def get_setting(key, default=None):
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key, value):
    conn = get_connection()
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value))
    )
    conn.commit()
    conn.close()


# ── Expenses ──────────────────────────────────────────────────────────────────

def add_expense(description, amount, currency, category, exp_date, notes=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO expenses (description, amount, currency, category, date, notes) VALUES (?,?,?,?,?,?)",
        (description, amount, currency, category, exp_date, notes)
    )
    conn.commit()
    conn.close()


def get_expenses(start_date, end_date, limit=None):
    conn = get_connection()
    q = "SELECT * FROM expenses WHERE date BETWEEN ? AND ? ORDER BY date DESC, id DESC"
    params = [str(start_date), str(end_date)]
    if limit:
        q += f" LIMIT {limit}"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_expense(exp_id):
    conn = get_connection()
    conn.execute("DELETE FROM expenses WHERE id = ?", (exp_id,))
    conn.commit()
    conn.close()


def update_expense(exp_id, **kwargs):
    conn = get_connection()
    fields = ", ".join(f"{k}=?" for k in kwargs)
    conn.execute(f"UPDATE expenses SET {fields} WHERE id=?", list(kwargs.values()) + [exp_id])
    conn.commit()
    conn.close()


# ── Budgets ───────────────────────────────────────────────────────────────────

def add_budget(category, amount, currency):
    conn = get_connection()
    conn.execute(
        "INSERT INTO budgets (category, amount, currency) VALUES (?,?,?) "
        "ON CONFLICT(category) DO UPDATE SET amount=excluded.amount, currency=excluded.currency, updated_at=datetime('now')",
        (category, amount, currency)
    )
    conn.commit()
    conn.close()


def get_budgets():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM budgets ORDER BY category").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Analytics ─────────────────────────────────────────────────────────────────

def get_summary(start_date, end_date):
    conn = get_connection()
    row = conn.execute(
        "SELECT COALESCE(SUM(amount),0) as total, COUNT(*) as count "
        "FROM expenses WHERE date BETWEEN ? AND ?",
        (str(start_date), str(end_date))
    ).fetchone()
    conn.close()
    return dict(row) if row else {"total": 0, "count": 0}


def get_category_totals(start_date, end_date):
    conn = get_connection()
    rows = conn.execute(
        "SELECT category, SUM(amount) as total FROM expenses "
        "WHERE date BETWEEN ? AND ? GROUP BY category ORDER BY total DESC",
        (str(start_date), str(end_date))
    ).fetchall()
    conn.close()
    return pd.DataFrame([dict(r) for r in rows]) if rows else pd.DataFrame(columns=["category", "total"])


def get_monthly_trend(months=6):
    conn = get_connection()
    rows = conn.execute(
        "SELECT strftime('%Y-%m', date) as month, SUM(amount) as total "
        "FROM expenses GROUP BY month ORDER BY month DESC LIMIT ?",
        (months,)
    ).fetchall()
    conn.close()
    df = pd.DataFrame([dict(r) for r in rows]) if rows else pd.DataFrame(columns=["month", "total"])
    if not df.empty:
        df = df.sort_values("month")
        df["month"] = pd.to_datetime(df["month"]).dt.strftime("%b %Y")
    return df


def get_spending_alerts(start_date, end_date):
    budgets = get_budgets()
    cat_totals = get_category_totals(start_date, end_date)
    alerts = []

    if budgets and not cat_totals.empty:
        for b in budgets:
            row = cat_totals[cat_totals["category"] == b["category"]]
            if not row.empty:
                spent = row["total"].values[0]
                pct = spent / b["amount"] * 100
                if pct >= 100:
                    alerts.append(f"You've exceeded your {b['category']} budget! (spent {spent:,.2f} of {b['amount']:,.2f})")
                elif pct >= 80:
                    alerts.append(f"You're at {pct:.0f}% of your {b['category']} budget.")
    return alerts
