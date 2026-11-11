"""
db.py — SQLite database setup for WeekPlate.
Compatible with local environments AND Vercel serverless (uses /tmp on Vercel).
Guarantees tables and default seed data exist on every connection.
"""

import sqlite3
import os

if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/weekplate.db"
else:
    DB_PATH = os.environ.get("WEEKPLATE_DB", "weekplate.db")


def get_conn() -> sqlite3.Connection:
    """Return an active connection, ensuring tables exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init():
    """Create all tables and auto-seed sample reviewer data if empty."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                email       TEXT    NOT NULL,
                token       TEXT    NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS meal_plans (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id),
                week_start  TEXT    NOT NULL,
                servings    INTEGER NOT NULL DEFAULT 2,
                slug        TEXT    NOT NULL UNIQUE,
                created_at  TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS meals (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id      INTEGER NOT NULL REFERENCES meal_plans(id) ON DELETE CASCADE,
                day          TEXT    NOT NULL,
                name         TEXT    NOT NULL,
                minutes      INTEGER NOT NULL DEFAULT 30,
                recipe_notes TEXT    NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS ingredients (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                meal_id INTEGER NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
                name    TEXT    NOT NULL,
                qty     REAL    NOT NULL DEFAULT 1.0,
                unit    TEXT    NOT NULL DEFAULT 'unit'
            );

            CREATE TABLE IF NOT EXISTS grocery_items (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id   INTEGER NOT NULL REFERENCES meal_plans(id) ON DELETE CASCADE,
                name      TEXT    NOT NULL,
                total_qty REAL    NOT NULL DEFAULT 0.0,
                unit      TEXT    NOT NULL DEFAULT 'unit',
                checked   INTEGER NOT NULL DEFAULT 0
            );
        """)
        conn.commit()

        # Always ensure testtoken123 reviewer account exists
        test_user = conn.execute("SELECT id FROM users WHERE token = 'testtoken123'").fetchone()
        if not test_user:
            _seed_default_data(conn)
    finally:
        conn.close()


def _seed_default_data(conn):
    """Seed reviewer account and sample meal plan on cold starts."""
    try:
        cur = conn.execute(
            "INSERT INTO users (email, token) VALUES (?, ?)",
            ("reviewer@weekplate.com", "testtoken123"),
        )
        uid = cur.lastrowid

        cur = conn.execute(
            "INSERT INTO meal_plans (user_id, week_start, servings, slug, created_at) VALUES (?, ?, ?, ?, ?)",
            (uid, "2026-11-16", 4, "sample_family_plan", "2026-11-11T09:00:00Z"),
        )
        pid = cur.lastrowid

        # Monday
        m1 = conn.execute(
            "INSERT INTO meals (plan_id, day, name, minutes, recipe_notes) VALUES (?, ?, ?, ?, ?)",
            (pid, "Monday", "Chickpea & Spinach Coconut Curry", 35, "One-pot curry with basmati rice."),
        ).lastrowid
        conn.executemany(
            "INSERT INTO ingredients (meal_id, name, qty, unit) VALUES (?, ?, ?, ?)",
            [
                (m1, "chickpeas", 2.0, "can"),
                (m1, "coconut milk", 1.0, "can"),
                (m1, "spinach", 1.0, "bunch"),
                (m1, "garlic", 3.0, "cloves"),
                (m1, "onion", 1.0, "medium"),
            ],
        )

        # Tuesday
        m2 = conn.execute(
            "INSERT INTO meals (plan_id, day, name, minutes, recipe_notes) VALUES (?, ?, ?, ?, ?)",
            (pid, "Tuesday", "Black Bean & Corn Sheet-Pan Fajitas", 30, "Roast on high heat in oven."),
        ).lastrowid
        conn.executemany(
            "INSERT INTO ingredients (meal_id, name, qty, unit) VALUES (?, ?, ?, ?)",
            [
                (m2, "black beans", 1.0, "can"),
                (m2, "bell peppers", 3.0, "medium"),
                (m2, "tortillas", 8.0, "count"),
                (m2, "lime", 2.0, "count"),
            ],
        )

        # Wednesday
        m3 = conn.execute(
            "INSERT INTO meals (plan_id, day, name, minutes, recipe_notes) VALUES (?, ?, ?, ?, ?)",
            (pid, "Wednesday", "Creamy Tomato & Basil Chickpea Pasta", 25, "Toss penne with crushed tomatoes."),
        ).lastrowid
        conn.executemany(
            "INSERT INTO ingredients (meal_id, name, qty, unit) VALUES (?, ?, ?, ?)",
            [
                (m3, "chickpeas", 1.0, "can"),
                (m3, "penne pasta", 1.0, "box"),
                (m3, "crushed tomatoes", 1.0, "can"),
                (m3, "garlic", 2.0, "cloves"),
            ],
        )

        groceries = [
            ("Chickpeas", 3.0, "can", 0),
            ("Garlic", 5.0, "cloves", 0),
            ("Coconut Milk", 1.0, "can", 0),
            ("Spinach", 1.0, "bunch", 0),
            ("Onion", 1.0, "medium", 0),
            ("Black Beans", 1.0, "can", 0),
            ("Bell Peppers", 3.0, "medium", 0),
            ("Tortillas", 8.0, "count", 0),
            ("Lime", 2.0, "count", 0),
            ("Penne Pasta", 1.0, "box", 0),
            ("Crushed Tomatoes", 1.0, "can", 0),
        ]
        for name, qty, unit, chk in groceries:
            conn.execute(
                "INSERT INTO grocery_items (plan_id, name, total_qty, unit, checked) VALUES (?, ?, ?, ?, ?)",
                (pid, name, qty, unit, chk),
            )

        conn.commit()
    except Exception:
        pass
