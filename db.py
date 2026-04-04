import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "nexus_budget.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS expenses (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount    REAL NOT NULL,
            currency  TEXT NOT NULL DEFAULT 'USD',
            category  TEXT NOT NULL,
            date      TEXT NOT NULL,
            notes     TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS budgets (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            category  TEXT NOT NULL UNIQUE,
            amount    REAL NOT NULL,
            currency  TEXT NOT NULL DEFAULT 'USD',
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
    """)

    # Migration: strip emoji prefixes from category names
    _EMOJI_CATS = {
        "\U0001f354 Food & Dining": "Food & Dining",
        "\U0001f3e0 Housing & Rent": "Housing & Rent",
        "\U0001f697 Transport": "Transport",
        "\U0001f48a Health & Wellness": "Health & Wellness",
        "\U0001f3ae Entertainment": "Entertainment",
        "\U0001f6cd Shopping": "Shopping",
        "\U0001f4da Education": "Education",
        "\u2708\ufe0f Travel": "Travel",
        "\U0001f4a1 Utilities": "Utilities",
        "\U0001f4bc Business": "Business",
        "\U0001f381 Gifts & Donations": "Gifts & Donations",
        "\U0001f4f1 Subscriptions": "Subscriptions",
        "\U0001f3cb Fitness": "Fitness",
        "\U0001f43e Pets": "Pets",
        "\U0001f527 Other": "Other",
    }
    for old_cat, new_cat in _EMOJI_CATS.items():
        conn.execute("UPDATE expenses SET category = ? WHERE category = ?", (new_cat, old_cat))
        conn.execute("UPDATE budgets SET category = ? WHERE category = ?", (new_cat, old_cat))

    conn.commit()
    conn.close()
