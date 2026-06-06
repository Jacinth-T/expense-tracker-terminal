"""
Personal Expense Tracker
Main entry point — menu loop and user interaction.
"""

from datetime import date
from database import (
    initialize_db,
    add_expense,
    get_all_expenses,
    get_expenses_by_category,
    get_expenses_by_date_range,
    get_monthly_summary,
    get_top_category,
    get_daily_trend,
    get_budget,
    set_budget,
    delete_expense,
    get_categories,
)
from reports import (
    export_to_csv,
    plot_category_pie,
    plot_daily_trend,
    print_table,
)

# Default user ID (seeded on initialize_db)
USER_ID = 1


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def print_header():
    print("\n" + "=" * 44)
    print("       \U0001f4b8  Personal Expense Tracker")
    print("=" * 44)
    print("  1. Add Expense")
    print("  2. View All Expenses")
    print("  3. Search by Category")
    print("  4. Search by Date Range")
    print("  5. Monthly Summary")
    print("  6. Budget Tracker")
    print("  7. Export Report (CSV)")
    print("  8. Generate Charts")
    print("  9. Delete an Expense")
    print(" 10. Exit")
    print("=" * 44)


def input_date(prompt="Date (YYYY-MM-DD, Enter = today): "):
    """Prompts for a date string; defaults to today if blank."""
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return str(date.today())
        try:
            date.fromisoformat(raw)   # validates format
            return raw
        except ValueError:
            print("  [!] Invalid date format. Please use YYYY-MM-DD.")


def input_month_year():
    """Prompts for month and year separately; defaults to current month/year."""
    today = date.today()
    try:
        month_raw = input(f"  Month (1-12, Enter = {today.month}): ").strip()
        month = int(month_raw) if month_raw else today.month
        year_raw = input(f"  Year  (YYYY,   Enter = {today.year}): ").strip()
        year = int(year_raw) if year_raw else today.year
        if not (1 <= month <= 12):
            raise ValueError
        return month, year
    except ValueError:
        print("  [!] Invalid month/year. Using current month/year.")
        return today.month, today.year


def show_category_menu():
    """Prints numbered category list and returns the list of category rows."""
    cats = get_categories()
    print("  Categories:")
    for cat in cats:
        print(f"    {cat['id']}. {cat['name']}")
    return cats


def pick_category():
    """Shows category menu and returns (category_id, category_name)."""
    cats = show_category_menu()
    while True:
        raw = input("  Enter category number: ").strip()
        try:
            choice = int(raw)
            for cat in cats:
                if cat["id"] == choice:
                    return cat["id"], cat["name"]
            print("  [!] Invalid choice.")
        except ValueError:
            print("  [!] Please enter a number.")


# ---------------------------------------------------------------------------
# Menu option handlers
# ---------------------------------------------------------------------------

def handle_add_expense():
    print("\n--- Add Expense ---")
    category_id, category_name = pick_category()

    while True:
        try:
            amount = float(input("  Amount: ").strip())
            if amount <= 0:
                raise ValueError
            break
        except ValueError:
            print("  [!] Please enter a positive number.")

    description = input("  Description (optional): ").strip()
    expense_date = input_date()

    add_expense(USER_ID, category_id, amount, description, expense_date)
    print(f"  \u2713 Expense of \u20b9{amount:.2f} in '{category_name}' added for {expense_date}.")


def handle_view_all():
    print("\n--- All Expenses ---")
    rows = get_all_expenses(USER_ID)
    headers = ["ID", "Category", "Amount (₹)", "Description", "Date", "Recorded At"]
    print_table(rows, headers)


def handle_search_category():
    print("\n--- Search by Category ---")
    _, category_name = pick_category()
    rows = get_expenses_by_category(USER_ID, category_name)
    headers = ["ID", "Category", "Amount (₹)", "Description", "Date"]
    print(f"\n  Expenses in '{category_name}':")
    print_table(rows, headers)


def handle_date_range():
    print("\n--- Search by Date Range ---")
    start = input_date("  Start date (YYYY-MM-DD): ")
    end = input_date("  End date   (YYYY-MM-DD): ")
    if start > end:
        print("  [!] Start date must be before end date.")
        return
    rows = get_expenses_by_date_range(USER_ID, start, end)
    headers = ["ID", "Category", "Amount (₹)", "Description", "Date"]
    print(f"\n  Expenses from {start} to {end}:")
    print_table(rows, headers)


def handle_monthly_summary():
    print("\n--- Monthly Summary ---")
    month, year = input_month_year()

    summary = get_monthly_summary(USER_ID, year, month)
    top = get_top_category(USER_ID, year, month)
    budget = get_budget(USER_ID)
    grand_total = sum(row["total"] for row in summary) if summary else 0

    print(f"\n  Summary for {month:02d}/{year}:")
    headers = ["Category", "Total (₹)"]
    print_table(summary, headers)

    print(f"\n  Grand Total : \u20b9{grand_total:.2f}")
    if top:
        print(f"  Top Category: {top['name']} (\u20b9{top['total']:.2f})")

    if budget > 0:
        pct = (grand_total / budget) * 100
        bar_filled = int(pct / 5)   # each block = 5%
        bar = "\u2588" * bar_filled + "\u2591" * (20 - min(bar_filled, 20))
        status = "OVER BUDGET \u26a0\ufe0f" if pct > 100 else "within budget \u2705"
        print(f"\n  Budget      : \u20b9{budget:.2f}")
        print(f"  Used        : [{bar}] {pct:.1f}%  ({status})")
    else:
        print("\n  (No budget set — use option 6 to set one)")


def handle_budget_tracker():
    print("\n--- Budget Tracker ---")
    budget = get_budget(USER_ID)
    print(f"  Current monthly budget: \u20b9{budget:.2f}")

    update = input("  Update budget? (y/N): ").strip().lower()
    if update == "y":
        while True:
            try:
                new_budget = float(input("  New monthly budget: \u20b9").strip())
                if new_budget < 0:
                    raise ValueError
                set_budget(USER_ID, new_budget)
                budget = new_budget
                print(f"  \u2713 Budget updated to \u20b9{new_budget:.2f}.")
                break
            except ValueError:
                print("  [!] Please enter a non-negative number.")

    # Show current month spend vs budget
    today = date.today()
    summary = get_monthly_summary(USER_ID, today.year, today.month)
    spent = sum(row["total"] for row in summary) if summary else 0
    remaining = budget - spent

    print(f"\n  This month ({today.month:02d}/{today.year}):")
    print(f"    Spent     : \u20b9{spent:.2f}")
    print(f"    Budget    : \u20b9{budget:.2f}")

    if budget > 0:
        pct = (spent / budget) * 100
        bar_filled = int(pct / 5)
        bar = "\u2588" * bar_filled + "\u2591" * (20 - min(bar_filled, 20))
        print(f"    Used      : [{bar}] {pct:.1f}%")
        if remaining >= 0:
            print(f"    Remaining : \u20b9{remaining:.2f}  \u2705")
        else:
            print(f"    Over by   : \u20b9{abs(remaining):.2f}  \u26a0\ufe0f")
    else:
        print("    (Set a budget to see % used)")


def handle_export_csv():
    print("\n--- Export Report (CSV) ---")
    rows = get_all_expenses(USER_ID)
    if not rows:
        print("  [!] No expenses to export.")
        return

    default_name = f"expenses_{date.today()}"
    raw = input(f"  Filename (Enter = '{default_name}'): ").strip()
    filename = raw if raw else default_name

    path = export_to_csv(rows, filename)
    print(f"  \u2713 Report saved to: {path}")


def handle_generate_charts():
    print("\n--- Generate Charts ---")
    print("  1. Spending by Category (Pie Chart)")
    print("  2. Daily Spending Trend (Line Chart)")
    choice = input("  Choose (1/2): ").strip()

    month, year = input_month_year()

    if choice == "1":
        summary = get_monthly_summary(USER_ID, year, month)
        if not summary:
            print("  [!] No data for that month.")
            return
        path = plot_category_pie(summary, month, year)
        if path:
            print(f"  \u2713 Pie chart saved to: {path}")

    elif choice == "2":
        trend = get_daily_trend(USER_ID, year, month)
        if not trend:
            print("  [!] No data for that month.")
            return
        path = plot_daily_trend(trend, month, year)
        if path:
            print(f"  \u2713 Line chart saved to: {path}")

    else:
        print("  [!] Invalid choice.")


def handle_delete_expense():
    print("\n--- Delete an Expense ---")
    rows = get_all_expenses(USER_ID)
    if not rows:
        print("  [!] No expenses to delete.")
        return

    headers = ["ID", "Category", "Amount (₹)", "Description", "Date", "Recorded At"]
    print_table(rows, headers)

    while True:
        raw = input("\n  Enter Expense ID to delete (or 0 to cancel): ").strip()
        try:
            expense_id = int(raw)
            break
        except ValueError:
            print("  [!] Please enter a valid number.")

    if expense_id == 0:
        print("  Cancelled.")
        return

    # Confirm the ID exists in this user's expenses
    ids = [row["id"] for row in rows]
    if expense_id not in ids:
        print("  [!] Expense ID not found.")
        return

    confirm = input(f"  Delete expense #{expense_id}? (y/N): ").strip().lower()
    if confirm == "y":
        delete_expense(expense_id)
        print(f"  \u2713 Expense #{expense_id} deleted.")
    else:
        print("  Cancelled.")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    initialize_db()

    print("\nWelcome to Personal Expense Tracker!")

    while True:
        print_header()
        choice = input("  Enter your choice: ").strip()

        if choice == "1":
            handle_add_expense()
        elif choice == "2":
            handle_view_all()
        elif choice == "3":
            handle_search_category()
        elif choice == "4":
            handle_date_range()
        elif choice == "5":
            handle_monthly_summary()
        elif choice == "6":
            handle_budget_tracker()
        elif choice == "7":
            handle_export_csv()
        elif choice == "8":
            handle_generate_charts()
        elif choice == "9":
            handle_delete_expense()
        elif choice == "10":
            print("\nGoodbye! \U0001f44b\n")
            break
        else:
            print("  [!] Invalid choice. Please enter 1-10.")

        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    main()
