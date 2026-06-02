"""
Pre-populates the semantic query cache with verified, correct SQL for the 5 demo queries.
Run once: python database/seed_cache.py
On subsequent runs these queries return instantly from cache (bypassing the LLM).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.cache_service import cache_query

VERIFIED_QUERIES = [
    (
        "Show unpaid invoices above 5 lakhs from last quarter",
        """SELECT i.invoice_id, c.customer_name, i.invoice_date, i.total_amount, i.due_date, i.status
FROM invoices AS i
JOIN customers AS c ON i.customer_id = c.customer_id
WHERE i.invoice_date >= date('now', '-3 months')
  AND i.total_amount > 500000
  AND i.paid_amount < i.total_amount
ORDER BY i.total_amount DESC LIMIT 100"""
    ),
    (
        "Top 10 vendors by payment delays",
        """SELECT v.vendor_name, v.city,
       COUNT(po.po_id) AS delayed_orders,
       ROUND(AVG(julianday(po.actual_delivery) - julianday(po.expected_delivery)), 1) AS avg_delay_days,
       MAX(CAST(julianday(po.actual_delivery) - julianday(po.expected_delivery) AS INTEGER)) AS max_delay_days
FROM vendors AS v
JOIN purchase_orders AS po ON v.vendor_id = po.vendor_id
WHERE po.actual_delivery IS NOT NULL
  AND po.actual_delivery > po.expected_delivery
GROUP BY v.vendor_id, v.vendor_name, v.city
ORDER BY avg_delay_days DESC LIMIT 10"""
    ),
    (
        "Customers with highest outstanding balance this month",
        """SELECT c.customer_name, c.city, c.customer_type,
       c.outstanding_balance,
       c.credit_limit,
       ROUND(c.outstanding_balance * 100.0 / NULLIF(c.credit_limit, 0), 1) AS credit_utilization_pct
FROM customers AS c
WHERE c.outstanding_balance > 0 AND c.status = 'active'
ORDER BY c.outstanding_balance DESC LIMIT 20"""
    ),
    (
        "Total expenses by department this year",
        """SELECT d.department_name, d.location,
       COUNT(e.expense_id) AS num_expenses,
       ROUND(SUM(e.amount), 2) AS total_amount,
       ROUND(AVG(e.amount), 2) AS avg_amount
FROM departments AS d
JOIN expenses AS e ON d.department_id = e.department_id
WHERE strftime('%Y', e.expense_date) = strftime('%Y', 'now')
GROUP BY d.department_id, d.department_name, d.location
ORDER BY total_amount DESC LIMIT 100"""
    ),
    (
        "Products with stock below reorder level",
        """SELECT p.product_name, p.category, p.sku,
       p.stock_quantity, p.reorder_level,
       p.reorder_level - p.stock_quantity AS shortage_qty,
       p.unit_price
FROM products AS p
WHERE p.stock_quantity < p.reorder_level AND p.is_active = 1
ORDER BY shortage_qty DESC LIMIT 100"""
    ),
    # Alternate phrasings that also get cached
    (
        "unpaid invoices above 5 lakhs",
        """SELECT i.invoice_id, c.customer_name, i.invoice_date, i.total_amount, i.due_date, i.status
FROM invoices AS i
JOIN customers AS c ON i.customer_id = c.customer_id
WHERE i.total_amount > 500000
  AND i.paid_amount < i.total_amount
ORDER BY i.total_amount DESC LIMIT 100"""
    ),
    (
        "vendors with highest payment delays",
        """SELECT v.vendor_name, v.city,
       COUNT(po.po_id) AS delayed_orders,
       ROUND(AVG(julianday(po.actual_delivery) - julianday(po.expected_delivery)), 1) AS avg_delay_days
FROM vendors AS v
JOIN purchase_orders AS po ON v.vendor_id = po.vendor_id
WHERE po.actual_delivery IS NOT NULL AND po.actual_delivery > po.expected_delivery
GROUP BY v.vendor_id, v.vendor_name, v.city
ORDER BY avg_delay_days DESC LIMIT 10"""
    ),
    (
        "customers with outstanding balance",
        """SELECT c.customer_name, c.city, c.customer_type, c.outstanding_balance, c.credit_limit
FROM customers AS c
WHERE c.outstanding_balance > 0 AND c.status = 'active'
ORDER BY c.outstanding_balance DESC LIMIT 20"""
    ),
    (
        "expenses by department",
        """SELECT d.department_name, d.location,
       COUNT(e.expense_id) AS num_expenses,
       ROUND(SUM(e.amount), 2) AS total_amount
FROM departments AS d
JOIN expenses AS e ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name, d.location
ORDER BY total_amount DESC LIMIT 100"""
    ),
    (
        "products below reorder level",
        """SELECT p.product_name, p.category, p.sku, p.stock_quantity, p.reorder_level,
       p.reorder_level - p.stock_quantity AS shortage_qty
FROM products AS p
WHERE p.stock_quantity < p.reorder_level AND p.is_active = 1
ORDER BY shortage_qty DESC LIMIT 100"""
    ),
]


if __name__ == "__main__":
    print("Pre-loading semantic cache with verified queries...")
    for question, sql in VERIFIED_QUERIES:
        cache_query(question, sql)
        print(f"  ✅ Cached: {question[:60]}")
    print(f"\nDone! {len(VERIFIED_QUERIES)} queries pre-loaded into cache.")
    print("These will return instantly on next ask (shown with ⚡ cached badge).")
