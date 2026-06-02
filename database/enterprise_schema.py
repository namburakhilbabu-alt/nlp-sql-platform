"""
Enterprise database schema definitions.
Simulates a large enterprise ERP with finance, HR, procurement, sales, and inventory domains.
"""

SCHEMA_METADATA = [
    {
        "table_name": "customers",
        "description": "Master table of all customers including corporates and individuals. Contains contact details, credit limits, and account status.",
        "domain": "sales",
        "columns": [
            {"name": "customer_id", "type": "INTEGER", "pk": True, "description": "Unique customer identifier"},
            {"name": "customer_name", "type": "TEXT", "description": "Full name or company name of customer"},
            {"name": "email", "type": "TEXT", "description": "Customer email address"},
            {"name": "phone", "type": "TEXT", "description": "Contact phone number"},
            {"name": "city", "type": "TEXT", "description": "City of customer"},
            {"name": "state", "type": "TEXT", "description": "State of customer"},
            {"name": "country", "type": "TEXT", "description": "Country of customer"},
            {"name": "credit_limit", "type": "REAL", "description": "Maximum credit allowed for this customer in rupees"},
            {"name": "outstanding_balance", "type": "REAL", "description": "Current outstanding amount owed by customer"},
            {"name": "customer_type", "type": "TEXT", "description": "Type: retail, wholesale, corporate"},
            {"name": "status", "type": "TEXT", "description": "Account status: active, inactive, blacklisted"},
            {"name": "created_at", "type": "DATETIME", "description": "Date customer account was created"},
        ],
        "sample_questions": [
            "customers with highest outstanding balance",
            "top customers by credit limit",
            "inactive customers in Mumbai",
        ],
    },
    {
        "table_name": "vendors",
        "description": "Master table of all vendors and suppliers. Tracks vendor performance, payment terms, and contact info.",
        "domain": "procurement",
        "columns": [
            {"name": "vendor_id", "type": "INTEGER", "pk": True, "description": "Unique vendor identifier"},
            {"name": "vendor_name", "type": "TEXT", "description": "Vendor or supplier company name"},
            {"name": "contact_person", "type": "TEXT", "description": "Primary contact at vendor"},
            {"name": "email", "type": "TEXT", "description": "Vendor email"},
            {"name": "phone", "type": "TEXT", "description": "Vendor phone"},
            {"name": "city", "type": "TEXT", "description": "City of vendor"},
            {"name": "state", "type": "TEXT", "description": "State of vendor"},
            {"name": "payment_terms_days", "type": "INTEGER", "description": "Number of days for payment terms e.g. 30, 60, 90"},
            {"name": "avg_delivery_days", "type": "INTEGER", "description": "Average delivery time in days"},
            {"name": "rating", "type": "REAL", "description": "Vendor performance rating out of 5"},
            {"name": "status", "type": "TEXT", "description": "Vendor status: active, inactive, blacklisted"},
            {"name": "registered_at", "type": "DATETIME", "description": "Date vendor was registered"},
        ],
        "sample_questions": [
            "top 10 vendors by payment delays",
            "vendors with low ratings",
            "active vendors in Delhi",
        ],
    },
    {
        "table_name": "products",
        "description": "Product catalog containing all items sold or procured. Includes pricing, stock levels, and categorization.",
        "domain": "inventory",
        "columns": [
            {"name": "product_id", "type": "INTEGER", "pk": True, "description": "Unique product identifier"},
            {"name": "product_name", "type": "TEXT", "description": "Name of the product"},
            {"name": "category", "type": "TEXT", "description": "Product category e.g. Electronics, Furniture, Stationery"},
            {"name": "sub_category", "type": "TEXT", "description": "Sub-category of product"},
            {"name": "sku", "type": "TEXT", "description": "Stock keeping unit code"},
            {"name": "unit_price", "type": "REAL", "description": "Selling price per unit in rupees"},
            {"name": "cost_price", "type": "REAL", "description": "Purchase cost per unit in rupees"},
            {"name": "stock_quantity", "type": "INTEGER", "description": "Current stock available"},
            {"name": "reorder_level", "type": "INTEGER", "description": "Minimum stock level before reorder"},
            {"name": "unit_of_measure", "type": "TEXT", "description": "Unit e.g. pieces, kg, liters"},
            {"name": "is_active", "type": "INTEGER", "description": "1 if active, 0 if discontinued"},
        ],
        "sample_questions": [
            "products with stock below reorder level",
            "most expensive products",
            "products in Electronics category",
        ],
    },
    {
        "table_name": "invoices",
        "description": "All sales invoices raised to customers. Tracks invoice amounts, due dates, and payment status.",
        "domain": "finance",
        "columns": [
            {"name": "invoice_id", "type": "INTEGER", "pk": True, "description": "Unique invoice number"},
            {"name": "customer_id", "type": "INTEGER", "fk": "customers.customer_id", "description": "Customer this invoice belongs to"},
            {"name": "invoice_date", "type": "DATE", "description": "Date invoice was raised"},
            {"name": "due_date", "type": "DATE", "description": "Payment due date"},
            {"name": "total_amount", "type": "REAL", "description": "Total invoice amount in rupees"},
            {"name": "paid_amount", "type": "REAL", "description": "Amount paid so far"},
            {"name": "status", "type": "TEXT", "description": "Invoice status: paid, unpaid, partial, overdue"},
            {"name": "payment_date", "type": "DATE", "description": "Date full payment was received, null if unpaid"},
            {"name": "remarks", "type": "TEXT", "description": "Any remarks on the invoice"},
        ],
        "sample_questions": [
            "unpaid invoices above 5 lakhs",
            "overdue invoices from last quarter",
            "invoices due this month",
            "show unpaid invoices above 5 lakhs from last quarter",
        ],
    },
    {
        "table_name": "invoice_items",
        "description": "Line items of each invoice. Each row is one product in a sales invoice.",
        "domain": "finance",
        "columns": [
            {"name": "item_id", "type": "INTEGER", "pk": True, "description": "Unique line item id"},
            {"name": "invoice_id", "type": "INTEGER", "fk": "invoices.invoice_id", "description": "Invoice this item belongs to"},
            {"name": "product_id", "type": "INTEGER", "fk": "products.product_id", "description": "Product being sold"},
            {"name": "quantity", "type": "INTEGER", "description": "Quantity sold"},
            {"name": "unit_price", "type": "REAL", "description": "Price per unit at time of sale"},
            {"name": "discount_pct", "type": "REAL", "description": "Discount percentage applied"},
            {"name": "line_total", "type": "REAL", "description": "Total for this line after discount"},
        ],
        "sample_questions": [
            "top selling products",
            "products with highest discount",
        ],
    },
    {
        "table_name": "purchase_orders",
        "description": "Purchase orders raised to vendors for procuring goods. Tracks PO status, amounts, and delivery.",
        "domain": "procurement",
        "columns": [
            {"name": "po_id", "type": "INTEGER", "pk": True, "description": "Unique purchase order ID"},
            {"name": "vendor_id", "type": "INTEGER", "fk": "vendors.vendor_id", "description": "Vendor this PO is raised to"},
            {"name": "po_date", "type": "DATE", "description": "Date PO was raised"},
            {"name": "expected_delivery", "type": "DATE", "description": "Expected delivery date"},
            {"name": "actual_delivery", "type": "DATE", "description": "Actual delivery date, null if not yet delivered"},
            {"name": "total_amount", "type": "REAL", "description": "Total PO value in rupees"},
            {"name": "status", "type": "TEXT", "description": "PO status: pending, delivered, partial, cancelled"},
            {"name": "payment_status", "type": "TEXT", "description": "Payment status: paid, unpaid, partial"},
        ],
        "sample_questions": [
            "pending purchase orders",
            "vendors with delayed deliveries",
            "purchase orders above 10 lakhs",
        ],
    },
    {
        "table_name": "purchase_order_items",
        "description": "Line items of each purchase order.",
        "domain": "procurement",
        "columns": [
            {"name": "po_item_id", "type": "INTEGER", "pk": True, "description": "Unique PO line item id"},
            {"name": "po_id", "type": "INTEGER", "fk": "purchase_orders.po_id", "description": "Purchase order this item belongs to"},
            {"name": "product_id", "type": "INTEGER", "fk": "products.product_id", "description": "Product being purchased"},
            {"name": "quantity", "type": "INTEGER", "description": "Quantity ordered"},
            {"name": "unit_price", "type": "REAL", "description": "Agreed price per unit"},
            {"name": "line_total", "type": "REAL", "description": "Total for this line"},
        ],
        "sample_questions": [],
    },
    {
        "table_name": "payments",
        "description": "All payment transactions made by customers against invoices.",
        "domain": "finance",
        "columns": [
            {"name": "payment_id", "type": "INTEGER", "pk": True, "description": "Unique payment ID"},
            {"name": "invoice_id", "type": "INTEGER", "fk": "invoices.invoice_id", "description": "Invoice being paid"},
            {"name": "customer_id", "type": "INTEGER", "fk": "customers.customer_id", "description": "Customer making payment"},
            {"name": "payment_date", "type": "DATE", "description": "Date payment was received"},
            {"name": "amount", "type": "REAL", "description": "Payment amount in rupees"},
            {"name": "payment_mode", "type": "TEXT", "description": "Mode: NEFT, RTGS, cheque, cash, UPI"},
            {"name": "reference_no", "type": "TEXT", "description": "Bank reference or cheque number"},
        ],
        "sample_questions": [
            "payments received this month",
            "customers who paid via NEFT",
            "total payments by mode",
        ],
    },
    {
        "table_name": "employees",
        "description": "HR master table of all employees. Contains department, designation, salary, and joining details.",
        "domain": "hr",
        "columns": [
            {"name": "employee_id", "type": "INTEGER", "pk": True, "description": "Unique employee ID"},
            {"name": "first_name", "type": "TEXT", "description": "Employee first name"},
            {"name": "last_name", "type": "TEXT", "description": "Employee last name"},
            {"name": "email", "type": "TEXT", "description": "Work email"},
            {"name": "department_id", "type": "INTEGER", "fk": "departments.department_id", "description": "Department employee belongs to"},
            {"name": "designation", "type": "TEXT", "description": "Job title or designation"},
            {"name": "join_date", "type": "DATE", "description": "Date of joining"},
            {"name": "salary", "type": "REAL", "description": "Monthly salary in rupees"},
            {"name": "manager_id", "type": "INTEGER", "description": "Employee ID of direct manager"},
            {"name": "status", "type": "TEXT", "description": "Employment status: active, resigned, terminated"},
        ],
        "sample_questions": [
            "highest paid employees",
            "employees in Sales department",
            "employees who joined this year",
        ],
    },
    {
        "table_name": "departments",
        "description": "Company department master. Each department has a head and budget.",
        "domain": "hr",
        "columns": [
            {"name": "department_id", "type": "INTEGER", "pk": True, "description": "Unique department ID"},
            {"name": "department_name", "type": "TEXT", "description": "Name of department"},
            {"name": "head_employee_id", "type": "INTEGER", "description": "Employee ID of department head"},
            {"name": "budget", "type": "REAL", "description": "Annual department budget in rupees"},
            {"name": "location", "type": "TEXT", "description": "Office location of department"},
        ],
        "sample_questions": [
            "department with highest budget",
            "list all departments",
        ],
    },
    {
        "table_name": "sales_orders",
        "description": "Customer sales orders before invoice is raised. Tracks order to invoice lifecycle.",
        "domain": "sales",
        "columns": [
            {"name": "order_id", "type": "INTEGER", "pk": True, "description": "Unique sales order ID"},
            {"name": "customer_id", "type": "INTEGER", "fk": "customers.customer_id", "description": "Customer who placed order"},
            {"name": "employee_id", "type": "INTEGER", "fk": "employees.employee_id", "description": "Sales person handling order"},
            {"name": "order_date", "type": "DATE", "description": "Date order was placed"},
            {"name": "expected_delivery", "type": "DATE", "description": "Expected delivery date"},
            {"name": "total_amount", "type": "REAL", "description": "Total order value in rupees"},
            {"name": "status", "type": "TEXT", "description": "Order status: pending, confirmed, shipped, delivered, cancelled"},
            {"name": "invoice_id", "type": "INTEGER", "fk": "invoices.invoice_id", "description": "Invoice raised for this order, null if not yet invoiced"},
        ],
        "sample_questions": [
            "pending sales orders",
            "orders delivered this month",
            "top sales by employee",
        ],
    },
    {
        "table_name": "inventory_transactions",
        "description": "Records every stock movement — goods received, goods issued, returns, and adjustments.",
        "domain": "inventory",
        "columns": [
            {"name": "txn_id", "type": "INTEGER", "pk": True, "description": "Unique transaction ID"},
            {"name": "product_id", "type": "INTEGER", "fk": "products.product_id", "description": "Product involved"},
            {"name": "txn_type", "type": "TEXT", "description": "Type: receipt, issue, return, adjustment"},
            {"name": "quantity", "type": "INTEGER", "description": "Quantity moved (positive=in, negative=out)"},
            {"name": "txn_date", "type": "DATE", "description": "Date of transaction"},
            {"name": "reference_id", "type": "INTEGER", "description": "Related PO or sales order ID"},
            {"name": "warehouse", "type": "TEXT", "description": "Warehouse location"},
            {"name": "remarks", "type": "TEXT", "description": "Reason for transaction"},
        ],
        "sample_questions": [
            "stock movements this week",
            "items issued from warehouse",
        ],
    },
    {
        "table_name": "expenses",
        "description": "Company expense records by department. Tracks operational costs, travel, utilities, etc.",
        "domain": "finance",
        "columns": [
            {"name": "expense_id", "type": "INTEGER", "pk": True, "description": "Unique expense ID"},
            {"name": "department_id", "type": "INTEGER", "fk": "departments.department_id", "description": "Department that incurred expense"},
            {"name": "expense_category", "type": "TEXT", "description": "Category: travel, utilities, office, marketing, IT"},
            {"name": "amount", "type": "REAL", "description": "Expense amount in rupees"},
            {"name": "expense_date", "type": "DATE", "description": "Date of expense"},
            {"name": "approved_by", "type": "INTEGER", "description": "Employee ID who approved"},
            {"name": "status", "type": "TEXT", "description": "Status: pending, approved, rejected, paid"},
            {"name": "description", "type": "TEXT", "description": "Description of expense"},
        ],
        "sample_questions": [
            "top expenses by department",
            "total travel expenses this quarter",
            "pending expenses above 1 lakh",
        ],
    },
    {
        "table_name": "leaves",
        "description": "Employee leave records tracking approved, pending, and rejected leave applications.",
        "domain": "hr",
        "columns": [
            {"name": "leave_id", "type": "INTEGER", "pk": True, "description": "Unique leave record ID"},
            {"name": "employee_id", "type": "INTEGER", "fk": "employees.employee_id", "description": "Employee who applied"},
            {"name": "leave_type", "type": "TEXT", "description": "Type: sick, casual, earned, maternity"},
            {"name": "start_date", "type": "DATE", "description": "Leave start date"},
            {"name": "end_date", "type": "DATE", "description": "Leave end date"},
            {"name": "days", "type": "INTEGER", "description": "Total number of leave days"},
            {"name": "status", "type": "TEXT", "description": "Status: pending, approved, rejected"},
            {"name": "applied_at", "type": "DATETIME", "description": "When leave was applied"},
        ],
        "sample_questions": [
            "employees on leave this week",
            "pending leave applications",
        ],
    },
    {
        "table_name": "contracts",
        "description": "Customer and vendor contracts. Tracks contract value, validity, and renewal dates.",
        "domain": "sales",
        "columns": [
            {"name": "contract_id", "type": "INTEGER", "pk": True, "description": "Unique contract ID"},
            {"name": "party_type", "type": "TEXT", "description": "customer or vendor"},
            {"name": "party_id", "type": "INTEGER", "description": "ID of customer or vendor"},
            {"name": "contract_value", "type": "REAL", "description": "Total contract value in rupees"},
            {"name": "start_date", "type": "DATE", "description": "Contract start date"},
            {"name": "end_date", "type": "DATE", "description": "Contract end date"},
            {"name": "status", "type": "TEXT", "description": "Status: active, expired, terminated"},
            {"name": "renewal_date", "type": "DATE", "description": "Next renewal date"},
        ],
        "sample_questions": [
            "contracts expiring this month",
            "highest value active contracts",
        ],
    },
]

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    city TEXT,
    state TEXT,
    country TEXT DEFAULT 'India',
    credit_limit REAL DEFAULT 0,
    outstanding_balance REAL DEFAULT 0,
    customer_type TEXT DEFAULT 'retail',
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vendors (
    vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_name TEXT NOT NULL,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    city TEXT,
    state TEXT,
    payment_terms_days INTEGER DEFAULT 30,
    avg_delivery_days INTEGER DEFAULT 7,
    rating REAL DEFAULT 3.0,
    status TEXT DEFAULT 'active',
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    category TEXT,
    sub_category TEXT,
    sku TEXT UNIQUE,
    unit_price REAL DEFAULT 0,
    cost_price REAL DEFAULT 0,
    stock_quantity INTEGER DEFAULT 0,
    reorder_level INTEGER DEFAULT 10,
    unit_of_measure TEXT DEFAULT 'pieces',
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_name TEXT NOT NULL,
    head_employee_id INTEGER,
    budget REAL DEFAULT 0,
    location TEXT
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    department_id INTEGER REFERENCES departments(department_id),
    designation TEXT,
    join_date DATE,
    salary REAL DEFAULT 0,
    manager_id INTEGER,
    status TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER REFERENCES customers(customer_id),
    invoice_date DATE DEFAULT CURRENT_DATE,
    due_date DATE,
    total_amount REAL DEFAULT 0,
    paid_amount REAL DEFAULT 0,
    status TEXT DEFAULT 'unpaid',
    payment_date DATE,
    remarks TEXT
);

CREATE TABLE IF NOT EXISTS invoice_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER REFERENCES invoices(invoice_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER DEFAULT 1,
    unit_price REAL DEFAULT 0,
    discount_pct REAL DEFAULT 0,
    line_total REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER REFERENCES vendors(vendor_id),
    po_date DATE DEFAULT CURRENT_DATE,
    expected_delivery DATE,
    actual_delivery DATE,
    total_amount REAL DEFAULT 0,
    status TEXT DEFAULT 'pending',
    payment_status TEXT DEFAULT 'unpaid'
);

CREATE TABLE IF NOT EXISTS purchase_order_items (
    po_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    po_id INTEGER REFERENCES purchase_orders(po_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER DEFAULT 1,
    unit_price REAL DEFAULT 0,
    line_total REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER REFERENCES invoices(invoice_id),
    customer_id INTEGER REFERENCES customers(customer_id),
    payment_date DATE DEFAULT CURRENT_DATE,
    amount REAL DEFAULT 0,
    payment_mode TEXT DEFAULT 'NEFT',
    reference_no TEXT
);

CREATE TABLE IF NOT EXISTS sales_orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER REFERENCES customers(customer_id),
    employee_id INTEGER REFERENCES employees(employee_id),
    order_date DATE DEFAULT CURRENT_DATE,
    expected_delivery DATE,
    total_amount REAL DEFAULT 0,
    status TEXT DEFAULT 'pending',
    invoice_id INTEGER REFERENCES invoices(invoice_id)
);

CREATE TABLE IF NOT EXISTS inventory_transactions (
    txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER REFERENCES products(product_id),
    txn_type TEXT,
    quantity INTEGER DEFAULT 0,
    txn_date DATE DEFAULT CURRENT_DATE,
    reference_id INTEGER,
    warehouse TEXT DEFAULT 'Main',
    remarks TEXT
);

CREATE TABLE IF NOT EXISTS expenses (
    expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER REFERENCES departments(department_id),
    expense_category TEXT,
    amount REAL DEFAULT 0,
    expense_date DATE DEFAULT CURRENT_DATE,
    approved_by INTEGER,
    status TEXT DEFAULT 'pending',
    description TEXT
);

CREATE TABLE IF NOT EXISTS leaves (
    leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER REFERENCES employees(employee_id),
    leave_type TEXT,
    start_date DATE,
    end_date DATE,
    days INTEGER DEFAULT 1,
    status TEXT DEFAULT 'pending',
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contracts (
    contract_id INTEGER PRIMARY KEY AUTOINCREMENT,
    party_type TEXT,
    party_id INTEGER,
    contract_value REAL DEFAULT 0,
    start_date DATE,
    end_date DATE,
    status TEXT DEFAULT 'active',
    renewal_date DATE
);
"""
