# Personal Expense Tracker

A terminal-based personal expense tracking application built with Python and SQLite.

**Author:** Jacinth Terapalli

---

## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
python main.py
```

The SQLite database is created automatically at `data/expense_tracker.db` on first run.  
Exported CSVs and chart images are saved to the `reports/` folder.

---

## File Structure

```
expense-tracker/
├── main.py          → Menu loop + user interaction
├── database.py      → All DB functions (CRUD + queries)
├── reports.py       → Summary, charts, CSV export
├── schema.sql       → Raw SQL schema
├── requirements.txt → matplotlib, tabulate
├── data/            → expense_tracker.db (auto-created)
└── reports/         → Exported CSVs and chart PNGs
```

---

## Database Schema

### `users`
| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-incremented ID |
| name | TEXT | User's full name |
| email | TEXT UNIQUE | User's email address |
| monthly_budget | REAL | Monthly spending limit |
| created_at | TIMESTAMP | Record creation time |

### `categories`
| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-incremented ID |
| name | TEXT UNIQUE | Category name (Food, Transport, Utilities, Entertainment) |

### `expenses`
| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-incremented ID |
| user_id | INTEGER FK | References `users(id)` |
| category_id | INTEGER FK | References `categories(id)` |
| amount | REAL | Expense amount |
| description | TEXT | Optional note |
| expense_date | DATE | Date of the expense |
| created_at | TIMESTAMP | Record creation time |

---

## Key SQL Queries

### Monthly total per category — `SUM` + `GROUP BY`
```sql
SELECT c.name, SUM(e.amount) AS total
FROM expenses e JOIN categories c ON e.category_id = c.id
WHERE user_id = ? AND strftime('%Y-%m', expense_date) = ?
GROUP BY c.name ORDER BY total DESC;
```

### Daily spending trend — `SUM` + `GROUP BY` + `ORDER BY` + date filter
```sql
SELECT expense_date, SUM(amount) AS daily_total
FROM expenses
WHERE user_id = ? AND strftime('%Y-%m', expense_date) = ?
GROUP BY expense_date ORDER BY expense_date;
```

### Average daily spend — `AVG` over subquery
```sql
SELECT AVG(daily_total) FROM (
    SELECT SUM(amount) AS daily_total FROM expenses
    WHERE user_id = ? GROUP BY expense_date
);
```

### Top spending category — `SUM` + `GROUP BY` + `LIMIT`
```sql
SELECT c.name, SUM(e.amount) AS total
FROM expenses e JOIN categories c ON e.category_id = c.id
WHERE user_id = ? AND strftime('%Y-%m', expense_date) = ?
GROUP BY c.name ORDER BY total DESC LIMIT 1;
```

---

## Menu Options

| # | Option | Description |
|---|---|---|
| 1 | Add Expense | Pick category, enter amount, description, date |
| 2 | View All Expenses | Lists all expenses newest-first |
| 3 | Search by Category | Filter expenses by category |
| 4 | Search by Date Range | Filter between two dates (YYYY-MM-DD) |
| 5 | Monthly Summary | Totals per category + budget comparison |
| 6 | Budget Tracker | View/update budget, see % used this month |
| 7 | Export CSV | Saves all expenses to `reports/<name>.csv` |
| 8 | Generate Charts | Pie chart or line chart saved to `reports/` | (bonus objective)
| 9 | Delete an Expense | Remove an expense by ID |
| 10 | Exit | Quit the application |
