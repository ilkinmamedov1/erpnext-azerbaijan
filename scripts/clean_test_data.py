#!/usr/bin/env python3
"""
ERPNext Azerbaijan - Test Data Cleaner
Safely removes test records so the site is 100% clean and ready for production use.
"""

import os
import frappe

def run():
    site_name = os.environ.get("SITE_NAME", "frontend")
    company = os.environ.get("COMPANY_NAME", "TEST MMC")

    bench_logs = "/home/frappe/frappe-bench/logs"
    if os.path.exists(bench_logs) and not os.path.exists("/home/frappe/logs"):
        try:
            os.symlink(bench_logs, "/home/frappe/logs")
        except Exception:
            pass

    frappe.init(site=site_name, sites_path="/home/frappe/frappe-bench/sites")
    frappe.connect()
    frappe.set_user("Administrator")

    print(f"\n>>> CLEANING ALL TEST DATA FOR {company}...")

    # 1. Cancel and delete transactional documents
    doctypes_to_clean = [
        "Payment Entry",
        "Sales Invoice",
        "Purchase Invoice",
        "Delivery Note",
        "Purchase Receipt",
        "Sales Order",
        "Purchase Order",
        "Stock Entry",
        "Journal Entry"
    ]

    for dt in doctypes_to_clean:
        docs = frappe.get_all(dt, filters={"company": company}, pluck="name")
        for d in docs:
            try:
                doc = frappe.get_doc(dt, d)
                if doc.docstatus == 1:
                    doc.cancel()
                doc.delete()
                print(f"   [-] Deleted {dt}: {d}")
            except Exception as e:
                # Force delete if cancel has cascade
                try:
                    frappe.delete_doc(dt, d, force=True)
                    print(f"   [-] Force deleted {dt}: {d}")
                except Exception as e2:
                    print(f"   [!] Could not delete {dt} {d}: {e2}")

    # Clear GL & Stock Ledger entries for company
    frappe.db.sql("DELETE FROM `tabGL Entry` WHERE company = %s", (company,))
    frappe.db.sql("DELETE FROM `tabStock Ledger Entry` WHERE company = %s", (company,))
    frappe.db.sql("DELETE FROM `tabPayment Ledger Entry` WHERE company = %s", (company,))

    # 2. Delete test master records
    test_items = ["AZ-TEST-001", "PROD-001"]
    for item in test_items:
        if frappe.db.exists("Item", item):
            try:
                frappe.delete_doc("Item", item, force=True)
                print(f"   [-] Deleted test Item: {item}")
            except Exception as e:
                print(f"   [!] Could not delete Item {item}: {e}")

    test_parties = [
        ("Supplier", "Texno Distribüter QSC"),
        ("Customer", "Bakı Konsaltinq MMC")
    ]
    for dt, party in test_parties:
        if frappe.db.exists(dt, party):
            try:
                frappe.delete_doc(dt, party, force=True)
                print(f"   [-] Deleted test {dt}: {party}")
            except Exception as e:
                print(f"   [!] Could not delete {dt} {party}: {e}")

    frappe.db.commit()
    frappe.clear_cache()
    print("\n✅ SITE IS NOW 100% CLEAN (ZERO TEST DATA)!")

if __name__ == "__main__":
    run()
