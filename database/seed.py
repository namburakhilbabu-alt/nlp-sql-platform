"""
Seeds the SQLite database with realistic enterprise sample data.
Run: python database/seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from database.enterprise_schema import CREATE_TABLES_SQL
from app.core.config import settings
import random
from datetime import date, timedelta
import math

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})


def rand_date(start_days_ago: int, end_days_ago: int = 0) -> str:
    days = random.randint(end_days_ago, start_days_ago)
    return (date.today() - timedelta(days=days)).isoformat()


def seed_all():
    with engine.connect() as conn:
        for stmt in CREATE_TABLES_SQL.strip().split(";"):
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()

    cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune", "Kolkata", "Ahmedabad"]
    states = ["Maharashtra", "Delhi", "Karnataka", "Telangana", "Tamil Nadu", "Maharashtra", "West Bengal", "Gujarat"]
    departments_data = [
        ("Finance", 2500000, "Mumbai"),
        ("Sales", 3000000, "Delhi"),
        ("HR", 1500000, "Bangalore"),
        ("IT", 2000000, "Hyderabad"),
        ("Operations", 1800000, "Chennai"),
        ("Marketing", 2200000, "Mumbai"),
        ("Procurement", 1600000, "Pune"),
    ]
    designations = ["Manager", "Senior Analyst", "Analyst", "Director", "VP", "Executive", "Lead", "Consultant"]
    product_categories = [
        ("Electronics", "Laptops"), ("Electronics", "Phones"), ("Electronics", "Accessories"),
        ("Furniture", "Chairs"), ("Furniture", "Desks"), ("Stationery", "Pens"),
        ("Stationery", "Paper"), ("IT", "Software"), ("IT", "Hardware"),
    ]
    expense_cats = ["travel", "utilities", "office", "marketing", "IT"]
    leave_types = ["sick", "casual", "earned", "maternity"]
    payment_modes = ["NEFT", "RTGS", "cheque", "cash", "UPI"]

    with engine.connect() as conn:
        # Departments
        for name, budget, loc in departments_data:
            conn.execute(text(
                "INSERT OR IGNORE INTO departments (department_name, budget, location) VALUES (:n, :b, :l)"
            ), {"n": name, "b": budget, "l": loc})
        conn.commit()

        # Employees (50)
        for i in range(1, 51):
            dept_id = random.randint(1, len(departments_data))
            conn.execute(text("""
                INSERT INTO employees (first_name, last_name, email, department_id, designation, join_date, salary, status)
                VALUES (:fn, :ln, :em, :di, :des, :jd, :sal, :st)
            """), {
                "fn": f"Employee{i}", "ln": f"Last{i}",
                "em": f"emp{i}@company.com", "di": dept_id,
                "des": random.choice(designations),
                "jd": rand_date(2000, 30),
                "sal": random.randint(30000, 200000),
                "st": random.choice(["active", "active", "active", "resigned"]),
            })
        conn.commit()

        # Customers (100)
        for i in range(1, 101):
            city_i = random.randint(0, len(cities) - 1)
            conn.execute(text("""
                INSERT INTO customers (customer_name, email, phone, city, state, credit_limit, outstanding_balance, customer_type, status)
                VALUES (:cn, :em, :ph, :ci, :st, :cl, :ob, :ct, :s)
            """), {
                "cn": f"Customer Corp {i}", "em": f"cust{i}@email.com",
                "ph": f"98{random.randint(10000000,99999999)}",
                "ci": cities[city_i], "st": states[city_i],
                "cl": random.choice([500000, 1000000, 2000000, 5000000]),
                "ob": random.randint(0, 1500000),
                "ct": random.choice(["retail", "wholesale", "corporate"]),
                "s": random.choice(["active", "active", "active", "inactive"]),
            })
        conn.commit()

        # Vendors (40)
        for i in range(1, 41):
            city_i = random.randint(0, len(cities) - 1)
            conn.execute(text("""
                INSERT INTO vendors (vendor_name, contact_person, email, phone, city, state, payment_terms_days, avg_delivery_days, rating, status)
                VALUES (:vn, :cp, :em, :ph, :ci, :st, :pt, :ad, :rt, :s)
            """), {
                "vn": f"Vendor Solutions {i}", "cp": f"Contact{i}",
                "em": f"vendor{i}@supplier.com",
                "ph": f"80{random.randint(10000000,99999999)}",
                "ci": cities[city_i], "st": states[city_i],
                "pt": random.choice([30, 45, 60, 90]),
                "ad": random.randint(3, 21),
                "rt": round(random.uniform(2.0, 5.0), 1),
                "s": random.choice(["active", "active", "inactive"]),
            })
        conn.commit()

        # Products (60)
        for i in range(1, 61):
            cat, sub = random.choice(product_categories)
            unit_price = random.randint(500, 150000)
            conn.execute(text("""
                INSERT INTO products (product_name, category, sub_category, sku, unit_price, cost_price, stock_quantity, reorder_level, unit_of_measure)
                VALUES (:pn, :cat, :sub, :sku, :up, :cp, :sq, :rl, :uom)
            """), {
                "pn": f"{sub} Model {i}", "cat": cat, "sub": sub,
                "sku": f"SKU-{cat[:3].upper()}-{i:04d}",
                "up": unit_price, "cp": int(unit_price * 0.7),
                "sq": random.randint(0, 500),
                "rl": random.randint(5, 50),
                "uom": "pieces",
            })
        conn.commit()

        # Invoices (200)
        invoice_statuses = ["paid", "unpaid", "partial", "overdue"]
        for i in range(1, 201):
            customer_id = random.randint(1, 100)
            invoice_date = rand_date(365, 1)
            total = random.randint(50000, 1500000)
            status = random.choice(invoice_statuses)
            paid = total if status == "paid" else (random.randint(0, total - 1) if status == "partial" else 0)
            due_date = (date.fromisoformat(invoice_date) + timedelta(days=30)).isoformat()
            payment_date = rand_date(30) if status == "paid" else None
            conn.execute(text("""
                INSERT INTO invoices (customer_id, invoice_date, due_date, total_amount, paid_amount, status, payment_date)
                VALUES (:ci, :id, :dd, :ta, :pa, :st, :pd)
            """), {
                "ci": customer_id, "id": invoice_date, "dd": due_date,
                "ta": total, "pa": paid, "st": status, "pd": payment_date,
            })
        conn.commit()

        # Payments (150)
        for i in range(1, 151):
            conn.execute(text("""
                INSERT INTO payments (invoice_id, customer_id, payment_date, amount, payment_mode, reference_no)
                VALUES (:ii, :ci, :pd, :am, :pm, :rn)
            """), {
                "ii": random.randint(1, 200), "ci": random.randint(1, 100),
                "pd": rand_date(180, 1),
                "am": random.randint(10000, 500000),
                "pm": random.choice(payment_modes),
                "rn": f"REF{random.randint(100000, 999999)}",
            })
        conn.commit()

        # Purchase Orders (100)
        for i in range(1, 101):
            vendor_id = random.randint(1, 40)
            po_date = rand_date(300, 1)
            expected = (date.fromisoformat(po_date) + timedelta(days=random.randint(7, 30))).isoformat()
            status = random.choice(["pending", "delivered", "partial", "cancelled"])
            actual = rand_date(100) if status == "delivered" else None
            conn.execute(text("""
                INSERT INTO purchase_orders (vendor_id, po_date, expected_delivery, actual_delivery, total_amount, status, payment_status)
                VALUES (:vi, :pd, :ed, :ad, :ta, :st, :ps)
            """), {
                "vi": vendor_id, "pd": po_date, "ed": expected, "ad": actual,
                "ta": random.randint(100000, 2000000),
                "st": status,
                "ps": random.choice(["paid", "unpaid", "partial"]),
            })
        conn.commit()

        # Expenses (80)
        for i in range(1, 81):
            dept_id = random.randint(1, len(departments_data))
            conn.execute(text("""
                INSERT INTO expenses (department_id, expense_category, amount, expense_date, status, description)
                VALUES (:di, :ec, :am, :ed, :st, :desc)
            """), {
                "di": dept_id,
                "ec": random.choice(expense_cats),
                "am": random.randint(5000, 300000),
                "ed": rand_date(180, 1),
                "st": random.choice(["pending", "approved", "approved", "paid"]),
                "desc": f"Expense item {i}",
            })
        conn.commit()

        # Leaves (60)
        for i in range(1, 61):
            emp_id = random.randint(1, 50)
            start = rand_date(90, 1)
            days = random.randint(1, 10)
            end = (date.fromisoformat(start) + timedelta(days=days - 1)).isoformat()
            conn.execute(text("""
                INSERT INTO leaves (employee_id, leave_type, start_date, end_date, days, status)
                VALUES (:ei, :lt, :sd, :ed, :d, :st)
            """), {
                "ei": emp_id,
                "lt": random.choice(leave_types),
                "sd": start, "ed": end, "d": days,
                "st": random.choice(["pending", "approved", "approved", "rejected"]),
            })
        conn.commit()

        # Contracts (30)
        for i in range(1, 31):
            party = random.choice(["customer", "vendor"])
            party_id = random.randint(1, 100 if party == "customer" else 40)
            start = rand_date(730, 30)
            end = (date.fromisoformat(start) + timedelta(days=365)).isoformat()
            conn.execute(text("""
                INSERT INTO contracts (party_type, party_id, contract_value, start_date, end_date, status)
                VALUES (:pt, :pi, :cv, :sd, :ed, :st)
            """), {
                "pt": party, "pi": party_id,
                "cv": random.randint(500000, 50000000),
                "sd": start, "ed": end,
                "st": random.choice(["active", "active", "expired"]),
            })
        conn.commit()

        # Sales Orders (120)
        order_statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
        for i in range(1, 121):
            customer_id = random.randint(1, 100)
            employee_id = random.randint(1, 50)
            order_date = rand_date(180, 1)
            expected = (date.fromisoformat(order_date) + timedelta(days=random.randint(3, 20))).isoformat()
            status = random.choice(order_statuses)
            invoice_id = random.randint(1, 200) if status == "delivered" else None
            conn.execute(text("""
                INSERT INTO sales_orders (customer_id, employee_id, order_date, expected_delivery, total_amount, status, invoice_id)
                VALUES (:ci, :ei, :od, :ed, :ta, :st, :ii)
            """), {
                "ci": customer_id, "ei": employee_id,
                "od": order_date, "ed": expected,
                "ta": random.randint(50000, 2000000),
                "st": status, "ii": invoice_id,
            })
        conn.commit()

        # Inventory Transactions (80)
        warehouses = ["Mumbai Main", "Delhi North", "Bangalore South", "Pune Central"]
        txn_types = ["receipt", "issue", "return", "adjustment"]
        for i in range(1, 81):
            conn.execute(text("""
                INSERT INTO inventory_transactions (product_id, txn_type, quantity, txn_date, warehouse, remarks)
                VALUES (:pi, :tt, :qty, :td, :wh, :rm)
            """), {
                "pi": random.randint(1, 60),
                "tt": random.choice(txn_types),
                "qty": random.randint(-50, 200),
                "td": rand_date(90, 1),
                "wh": random.choice(warehouses),
                "rm": f"Transaction {i}",
            })
        conn.commit()

    print("Database seeded successfully!")
    print("Tables: customers(100), vendors(40), products(60), invoices(200), payments(150)")
    print("        purchase_orders(100), expenses(80), employees(50), leaves(60), contracts(30)")
    print("        sales_orders(120), inventory_transactions(80)")


if __name__ == "__main__":
    seed_all()
