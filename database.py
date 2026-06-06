import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "expense_tracker.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_connection():
    """Returns a sqlite3 connection with row_factory set to sqlite3.Row."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_db():
    """Creates tables from schema.sql and seeds default categories and user."""
    conn = get_connection()
    try:
        with open(SCHEMA_PATH, "r") as f:
            schema = f.read()
        conn.executescript(schema)

        # Seed default categories
        categories = ["Food", "Transport", "Utilities", "Entertainment"]
        for cat in categories:
            conn.execute(
                "INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,)
            )

        # Seed a default user so the app works immediately
        conn.execute(
            "INSERT OR IGNORE INTO users (name, email, monthly_budget) VALUES (?, ?, ?)",
            ("Default User", "user@example.com", 0),
        )
        conn.commit()
    finally:
        conn.close()


def add_expense(user_id, category_id, amount, description, date):
    """Inserts a new expense record into the database."""
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO expenses (user_id, category_id, amount, description, expense_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, category_id, amount, description, date),
        )
        conn.commit()
    finally:
        conn.close()


def get_all_expenses(user_id):
    """Returns all expenses for a user joined with category name, newest first."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT e.id, c.name AS category, e.amount, e.description,
                   e.expense_date, e.created_at
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.user_id = ?
            ORDER BY e.expense_date DESC
            """,
            (user_id,),
        ).fetchall()
        return rows
    finally:
        conn.close()


def get_expenses_by_category(user_id, category_name):
    """Returns all expenses for a user filtered by category name."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT e.id, c.name AS category, e.amount, e.description,
                   e.expense_date
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.user_id = ? AND c.name = ?
            ORDER BY e.expense_date DESC
            """,
            (user_id, category_name),
        ).fetchall()
        return rows
    finally:
        conn.close()


def get_expenses_by_date_range(user_id, start, end):
    """Returns all expenses for a user within the given date range (inclusive)."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT e.id, c.name AS category, e.amount, e.description,
                   e.expense_date
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.user_id = ? AND e.expense_date BETWEEN ? AND ?
            ORDER BY e.expense_date DESC
            """,
            (user_id, start, end),
        ).fetchall()
        return rows
    finally:
        conn.close()


def get_monthly_summary(user_id, year, month):
    """Returns total amount spent per category for a given month/year."""
    period = f"{year}-{month:02d}"
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT c.name, SUM(e.amount) AS total
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.user_id = ? AND strftime('%Y-%m', e.expense_date) = ?
            GROUP BY c.name
            ORDER BY total DESC
            """,
            (user_id, period),
        ).fetchall()
        return rows
    finally:
        conn.close()


def get_top_category(user_id, year, month):
    """Returns the category with the highest spend in the given month/year."""
    period = f"{year}-{month:02d}"
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT c.name, SUM(e.amount) AS total
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.user_id = ? AND strftime('%Y-%m', e.expense_date) = ?
            GROUP BY c.name
            ORDER BY total DESC
            LIMIT 1
            """,
            (user_id, period),
        ).fetchone()
        return row
    finally:
        conn.close()


def get_daily_trend(user_id, year, month):
    """Returns day-by-day spending totals for a given month/year."""
    period = f"{year}-{month:02d}"
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT e.expense_date, SUM(e.amount) AS daily_total
            FROM expenses e
            WHERE e.user_id = ? AND strftime('%Y-%m', e.expense_date) = ?
            GROUP BY e.expense_date
            ORDER BY e.expense_date
            """,
            (user_id, period),
        ).fetchall()
        return rows
    finally:
        conn.close()


def get_budget(user_id):
    """Returns the monthly budget for the given user."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT monthly_budget FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return row["monthly_budget"] if row else 0
    finally:
        conn.close()


def set_budget(user_id, amount):
    """Updates the monthly budget for the given user."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE users SET monthly_budget = ? WHERE id = ?", (amount, user_id)
        )
        conn.commit()
    finally:
        conn.close()


def delete_expense(expense_id):
    """Deletes an expense record by its ID."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
    finally:
        conn.close()


def get_categories():
    """Returns all categories from the database."""
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM categories").fetchall()
        return rows
    finally:
        conn.close()
