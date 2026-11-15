#!/usr/bin/env python3
"""
ERPNext Azerbaijan Full Commercial Cycle & Ledger Audit Test
Runs:
1. Master Data: Item, Supplier, Customer
2. Purchase Workflow: Purchase Order -> Purchase Receipt -> Purchase Invoice (with 18% ƏDV) -> Bank Payment
3. Sales Workflow: Sales Order -> Delivery Note -> Sales Invoice (with 18% ƏDV) -> Customer Bank Receipt
4. Stock Movement: Material Transfer between warehouses
5. Cash Journal: Cash expense from Kassa (221.01)
6. GL Ledger & Stock Ledger Integrity Audit
"""

import os
import sys
import frappe
from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt, make_purchase_invoice
from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note, make_sales_invoice
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

def run():
    site_name = os.environ.get("SITE_NAME", "frontend")
    company = os.environ.get("COMPANY_NAME", "TEST MMC")

    # Ensure logs directory accessible
    bench_logs = "/home/frappe/frappe-bench/logs"
    if os.path.exists(bench_logs) and not os.path.exists("/home/frappe/logs"):
        try:
            os.symlink(bench_logs, "/home/frappe/logs")
        except Exception:
            pass

    site_logs = f"/home/frappe/frappe-bench/sites/{site_name}/logs"
    os.makedirs(site_logs, exist_ok=True)

    frappe.init(site=site_name, sites_path="/home/frappe/frappe-bench/sites")
    frappe.connect()
    frappe.set_user("Administrator")

    abbr = frappe.db.get_value("Company", company, "abbr") or "TM"

    print(f"\n=======================================================")
    print(f"🚀 STARTING AZERBAIJAN ERP WORKFLOW TESTS FOR {company} ({abbr})")
    print(f"=======================================================")

    # 1. Master Data
    print("\n>>> STEP 1: Creating/Verifying Master Data (Item, Supplier, Customer)...")
    item_code = "AZ-TEST-001"
    if not frappe.db.exists("Item", item_code):
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": item_code,
            "item_name": "Lenovo ThinkPad T14 Gen 4",
            "item_group": "All Item Groups",
            "stock_uom": "Ədəd",
            "is_stock_item": 1,
            "default_warehouse": f"Əsas Anbar (Mallar) - {abbr}"
        }).insert(ignore_permissions=True)
        print(f"   [+] Item created: {item.name}")
    else:
        print(f"   [i] Item {item_code} already exists.")

    supp_name = "Texno Distribüter QSC"
    if not frappe.db.exists("Supplier", supp_name):
        supp = frappe.get_doc({
            "doctype": "Supplier",
            "supplier_name": supp_name,
            "supplier_group": "Distributor",
            "tax_id": "1400123451"
        }).insert(ignore_permissions=True)
        print(f"   [+] Supplier created: {supp.name} (VÖEN: 1400123451)")
    else:
        print(f"   [i] Supplier {supp_name} exists.")

    cust_name = "Bakı Konsaltinq MMC"
    if not frappe.db.exists("Customer", cust_name):
        cust = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": cust_name,
            "customer_group": "Commercial",
            "customer_type": "Company",
            "tax_id": "9900987651"
        }).insert(ignore_permissions=True)
        print(f"   [+] Customer created: {cust.name} (VÖEN: 9900987651)")
    else:
        print(f"   [i] Customer {cust_name} exists.")
    frappe.db.commit()

    # 2. Purchase Workflow
    print("\n>>> STEP 2: Executing Purchase Workflow (AS -> MQ -> AQ -> ÖD)...")
    po = frappe.get_doc({
        "doctype": "Purchase Order",
        "company": company,
        "supplier": supp_name,
        "transaction_date": frappe.utils.today(),
        "schedule_date": frappe.utils.today(),
        "items": [{
            "item_code": item_code,
            "qty": 10,
            "rate": 1000.00,
            "schedule_date": frappe.utils.today(),
            "warehouse": f"Əsas Anbar (Mallar) - {abbr}"
        }],
        "taxes_and_charges": f"ƏDV 18% (Yerli alışlar) - {abbr}",
        "taxes": [{
            "charge_type": "On Net Total",
            "account_head": f"241.01 - ƏDV əvəzləşməsi - yerli alışlar - {abbr}",
            "rate": 18.0,
            "description": "ƏDV @ 18% (Əvəzləşdirilən)",
            "category": "Valuation and Total",
            "add_deduct_tax": "Add"
        }]
    }).insert(ignore_permissions=True)
    po.submit()
    frappe.db.commit()
    print(f"   [+] Purchase Order submitted: {po.name} (10 pcs @ 1000 ₼)")

    # Purchase Receipt (MQ)
    pr = make_purchase_receipt(po.name)
    pr.insert(ignore_permissions=True)
    pr.submit()
    frappe.db.commit()
    print(f"   [+] Purchase Receipt submitted: {pr.name} (Goods received into Əsas Anbar)")

    # Purchase Invoice (AQ)
    pi = make_purchase_invoice(po.name)
    pi.insert(ignore_permissions=True)
    pi.submit()
    frappe.db.commit()
    print(f"   [+] Purchase Invoice submitted: {pi.name} (Grand Total: {pi.grand_total} AZN)")

    # Payment to Supplier (ÖD)
    pe_supp = get_payment_entry("Purchase Invoice", pi.name)
    pe_supp.mode_of_payment = "Bank köçürməsi (AZN)"
    pe_supp.paid_from = f"223.01 - Bank hesabı - AZN (Əsas bank) - {abbr}"
    pe_supp.reference_no = "AZ-BANK-OUT-001"
    pe_supp.reference_date = frappe.utils.today()
    pe_supp.insert(ignore_permissions=True)
    pe_supp.submit()
    frappe.db.commit()
    print(f"   [+] Supplier Payment submitted: {pe_supp.name} (Paid: {pe_supp.paid_amount} AZN)")

    # 3. Sales Workflow
    print("\n>>> STEP 3: Executing Sales Workflow (SS -> TQ -> SQ -> ÖD)...")
    so = frappe.get_doc({
        "doctype": "Sales Order",
        "company": company,
        "customer": cust_name,
        "transaction_date": frappe.utils.today(),
        "delivery_date": frappe.utils.today(),
        "items": [{
            "item_code": item_code,
            "qty": 4,
            "rate": 1500.00,
            "delivery_date": frappe.utils.today(),
            "warehouse": f"Əsas Anbar (Mallar) - {abbr}"
        }],
        "taxes_and_charges": f"ƏDV 18% - {abbr}",
        "taxes": [{
            "charge_type": "On Net Total",
            "account_head": f"521.01 - ƏDV öhdəliyi - {abbr}",
            "rate": 18.0,
            "description": "ƏDV @ 18.0%"
        }]
    }).insert(ignore_permissions=True)
    so.submit()
    frappe.db.commit()
    print(f"   [+] Sales Order submitted: {so.name} (4 pcs @ 1500 ₼)")

    # Delivery Note (TQ)
    dn = make_delivery_note(so.name)
    dn.insert(ignore_permissions=True)
    dn.submit()
    frappe.db.commit()
    print(f"   [+] Delivery Note submitted: {dn.name} (Dispatched from warehouse)")

    # Sales Invoice (SQ)
    si = make_sales_invoice(so.name)
    si.income_account = f"601.02.01 - Mal satışı - pərakəndə - {abbr}"
    si.cost_center = f"Main - {abbr}"
    si.insert(ignore_permissions=True)
    si.submit()
    frappe.db.commit()
    print(f"   [+] Sales Invoice submitted: {si.name} (Grand Total: {si.grand_total} AZN)")

    # Payment Receipt from Customer (ÖD)
    pe_cust = get_payment_entry("Sales Invoice", si.name)
    pe_cust.mode_of_payment = "Bank köçürməsi (AZN)"
    pe_cust.paid_to = f"223.01 - Bank hesabı - AZN (Əsas bank) - {abbr}"
    pe_cust.reference_no = "AZ-BANK-IN-001"
    pe_cust.reference_date = frappe.utils.today()
    pe_cust.insert(ignore_permissions=True)
    pe_cust.submit()
    frappe.db.commit()
    print(f"   [+] Customer Receipt submitted: {pe_cust.name} (Received: {pe_cust.received_amount} AZN)")

    # 4. Warehouse Stock Transfer
    print("\n>>> STEP 4: Executing Warehouse Stock Transfer...")
    ste = frappe.get_doc({
        "doctype": "Stock Entry",
        "stock_entry_type": "Material Transfer",
        "company": company,
        "items": [{
            "item_code": item_code,
            "qty": 2,
            "s_warehouse": f"Əsas Anbar (Mallar) - {abbr}",
            "t_warehouse": f"Hazır Məhsul Anbarı - {abbr}"
        }]
    }).insert(ignore_permissions=True)
    ste.submit()
    frappe.db.commit()
    print(f"   [+] Stock Transfer submitted: {ste.name} (2 pcs moved to Hazır Məhsul Anbarı)")

    # 5. Cash Expense (Kassa Məxaric)
    print("\n>>> STEP 5: Executing Cash Expense Entry (Kassa 221.01 -> Xərc 721.19)...")
    je = frappe.get_doc({
        "doctype": "Journal Entry",
        "voucher_type": "Cash Entry",
        "company": company,
        "posting_date": frappe.utils.today(),
        "user_remark": "Ofis ləvazimatları xərci (Kassa)",
        "accounts": [
            {
                "account": f"721.19 - Digər inzibati xərclər - {abbr}",
                "debit_in_account_currency": 120.00,
                "cost_center": f"Main - {abbr}"
            },
            {
                "account": f"221.01 - Kassa - AZN - {abbr}",
                "credit_in_account_currency": 120.00
            }
        ]
    }).insert(ignore_permissions=True)
    je.submit()
    frappe.db.commit()
    print(f"   [+] Journal Entry submitted: {je.name} (120 AZN Kassa payment)")

    # 6. GL Ledger Integrity Audit
    print("\n>>> STEP 6: GENERAL LEDGER (BAŞ KİTAB) AUDIT:")
    gl_entries = frappe.db.sql("""
        SELECT account, SUM(debit) as total_debit, SUM(credit) as total_credit
        FROM `tabGL Entry`
        WHERE company = %s AND is_cancelled = 0
        GROUP BY account
        ORDER BY account
    """, (company,), as_dict=True)

    sum_debit = 0.0
    sum_credit = 0.0
    for gl in gl_entries:
        net = gl.total_debit - gl.total_credit
        sum_debit += float(gl.total_debit)
        sum_credit += float(gl.total_credit)
        print(f"   {gl.account:<60} | D: {gl.total_debit:>10.2f} ₼ | C: {gl.total_credit:>10.2f} ₼ | Net: {net:>10.2f} ₼")

    print(f"   {'TOTALS':<60} | D: {sum_debit:>10.2f} ₼ | C: {sum_credit:>10.2f} ₼ | Diff: {abs(sum_debit - sum_credit):>10.2f} ₼")
    assert abs(sum_debit - sum_credit) < 0.01, "FATAL: General Ledger does not balance!"

    # 7. Stock Balance Audit
    print("\n>>> STEP 7: STOCK BALANCE AUDIT (ANBAR QALIQLARI):")
    stock_qty = frappe.db.sql("""
        SELECT item_code, warehouse, SUM(actual_qty) as qty
        FROM `tabStock Ledger Entry`
        WHERE is_cancelled = 0
        GROUP BY item_code, warehouse
        ORDER BY warehouse
    """, as_dict=True)
    for s in stock_qty:
        print(f"   Məhsul: {s.item_code} | Anbar: {s.warehouse:<40} | Qalıq: {s.qty} Ədəd")

    print("\n=======================================================")
    print("✅ ALL WORKFLOW TESTS & ACCOUNTING AUDITS PASSED 100%!")
    print("=======================================================\n")

if __name__ == "__main__":
    run()
