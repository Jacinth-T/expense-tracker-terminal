import csv
import os

# Try importing optional libraries gracefully
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")


def _ensure_reports_dir():
    """Creates the reports directory if it does not exist."""
    os.makedirs(REPORTS_DIR, exist_ok=True)


def export_to_csv(expenses, filename):
    """
    Writes expense rows to reports/<filename>.csv using Python's csv module.
    Returns the full path of the saved file.
    """
    _ensure_reports_dir()
    filepath = os.path.join(REPORTS_DIR, f"{filename}.csv")

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if expenses:
            # sqlite3.Row supports keys()
            writer.writerow(expenses[0].keys())
            for row in expenses:
                writer.writerow(list(row))
        else:
            writer.writerow(["No data available"])

    return filepath


def plot_category_pie(summary_data, month, year):
    """
    Saves a pie chart of spending by category to
    reports/category_pie_<month>_<year>.png
    Returns the full path, or None if matplotlib is not installed.
    """
    if not MATPLOTLIB_AVAILABLE:
        print("  [!] matplotlib is not installed. Run: pip install matplotlib")
        return None

    _ensure_reports_dir()
    filepath = os.path.join(REPORTS_DIR, f"category_pie_{month:02d}_{year}.png")

    labels = [row["name"] for row in summary_data]
    sizes = [row["total"] for row in summary_data]

    if not labels:
        print("  [!] No data available to plot.")
        return None

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops={"edgecolor": "white"},
    )
    ax.set_title(f"Spending by Category — {month:02d}/{year}", fontsize=14)
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

    return filepath


def plot_daily_trend(trend_data, month, year):
    """
    Saves a line chart of daily spending to
    reports/daily_trend_<month>_<year>.png
    Returns the full path, or None if matplotlib is not installed.
    """
    if not MATPLOTLIB_AVAILABLE:
        print("  [!] matplotlib is not installed. Run: pip install matplotlib")
        return None

    _ensure_reports_dir()
    filepath = os.path.join(REPORTS_DIR, f"daily_trend_{month:02d}_{year}.png")

    dates = [row["expense_date"] for row in trend_data]
    totals = [row["daily_total"] for row in trend_data]

    if not dates:
        print("  [!] No data available to plot.")
        return None

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dates, totals, marker="o", linewidth=2, color="#4C72B0")
    ax.fill_between(dates, totals, alpha=0.15, color="#4C72B0")
    ax.set_title(f"Daily Spending Trend — {month:02d}/{year}", fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Amount (₹)")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

    return filepath


def print_table(rows, headers):
    """
    Pretty-prints a list of rows as a table using tabulate.
    Falls back to plain printing if tabulate is not installed.
    """
    if not rows:
        print("  (No records found)")
        return

    # Convert sqlite3.Row objects to plain lists
    data = [list(row) for row in rows]

    if TABULATE_AVAILABLE:
        print(tabulate(data, headers=headers, tablefmt="simple",
                       floatfmt=".2f"))
    else:
        # Fallback: plain columnar print
        col_widths = [len(h) for h in headers]
        for row in data:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        fmt = "  " + "  ".join(f"{{:<{w}}}" for w in col_widths)
        print(fmt.format(*headers))
        print("  " + "-" * (sum(col_widths) + 2 * len(col_widths)))
        for row in data:
            print(fmt.format(*[str(c) for c in row]))
