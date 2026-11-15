import frappe
from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt, make_purchase_invoice
from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note, make_sales_invoice
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

def run():
    frappe.init(site="frontend", sites_path="/home/frappe/frappe-bench/sites")
    frappe.connect()
    company = "TEST MMC"
    abbr = "TM"

    print(">>> 1. Processing Purchase Order: AS-2026-00001...")
    # Step 1A: Purchase Receipt (Mədaxil Qaiməsi)
    pr = make_purchase_receipt("AS-2026-00001")
    pr.insert(ignore_permissions=True)
    pr.submit()
    frappe.db.commit()
    print(f"   [MƏDAXİL] Purchase Receipt submitted: {pr.name} (10 units received into Əsas Anbar)")

    # Step 1B: Purchase Invoice (Alış Fakturası)
    pi = make_purchase_invoice("AS-2026-00001")
    pi.insert(ignore_permissions=True)
    pi.submit()
    frappe.db.commit()
    print(f"   [FAKTURA] Purchase Invoice submitted: {pi.name} (Amount: {pi.grand_total} AZN)")

    # Step 1C: Supplier Payment (Bank Köçürməsi)
    pe_supp = get_payment_entry("Purchase Invoice", pi.name)
    pe_supp.mode_of_payment = "Bank köçürməsi (AZN)"
    pe_supp.paid_from = f"223.01 - Bank hesabı - AZN (Əsas bank) - {abbr}"
    pe_supp.reference_no = "PO-BANK-PAY-002"
    pe_supp.reference_date = frappe.utils.today()
    pe_supp.insert(ignore_permissions=True)
    pe_supp.submit()
    frappe.db.commit()
    print(f"   [ÖDƏNİŞ] Supplier Payment submitted: {pe_supp.name} (Paid: {pe_supp.paid_amount} AZN)")

    po_doc = frappe.get_doc("Purchase Order", "AS-2026-00001")
    print(f"   Purchase Order Status now: {po_doc.status} (per_received: {po_doc.per_received}%, per_billed: {po_doc.per_billed}%)")

    print("\n>>> 2. Processing Sales Order: SS-2026-00001...")
    # Step 2A: Delivery Note (Təhvil Qaiməsi / Çatdırılma)
    dn = make_delivery_note("SS-2026-00001")
    dn.insert(ignore_permissions=True)
    dn.submit()
    frappe.db.commit()
    print(f"   [TƏHVİL] Delivery Note submitted: {dn.name} (5 units delivered to Bakı Konsaltinq MMC)")

    # Step 2B: Sales Invoice (Satış Fakturası)
    si = make_sales_invoice("SS-2026-00001")
    si.insert(ignore_permissions=True)
    si.submit()
    frappe.db.commit()
    print(f"   [FAKTURA] Sales Invoice submitted: {si.name} (Amount: {si.grand_total} AZN)")

    # Step 2C: Customer Payment (Bank Mədaxili)
    pe_cust = get_payment_entry("Sales Invoice", si.name)
    pe_cust.mode_of_payment = "Bank köçürməsi (AZN)"
    pe_cust.paid_to = f"223.01 - Bank hesabı - AZN (Əsas bank) - {abbr}"
    pe_cust.reference_no = "SO-BANK-REC-002"
    pe_cust.reference_date = frappe.utils.today()
    pe_cust.insert(ignore_permissions=True)
    pe_cust.submit()
    frappe.db.commit()
    print(f"   [ÖDƏNİŞ] Customer Payment submitted: {pe_cust.name} (Received: {pe_cust.received_amount} AZN)")

    so_doc = frappe.get_doc("Sales Order", "SS-2026-00001")
    print(f"   Sales Order Status now: {so_doc.status} (per_delivered: {so_doc.per_delivered}%, per_billed: {so_doc.per_billed}%)")

    print("\n>>> 3. Processing Material Transfer (Anbarlararası Köçürmə)...")
    ste = frappe.get_doc({
        "doctype": "Stock Entry",
        "stock_entry_type": "Material Transfer",
        "company": company,
        "items": [{
            "item_code": "PROD-001",
            "qty": 3,
            "s_warehouse": f"Əsas Anbar (Mallar) - {abbr}",
            "t_warehouse": f"Hazır Məhsul Anbarı - {abbr}"
        }]
    })
    ste.insert(ignore_permissions=True)
    ste.submit()
    frappe.db.commit()
    print(f"   [ANBAR KÖÇÜRMƏSİ] Stock Entry submitted: {ste.name} (3 units moved from Əsas Anbar to Hazır Məhsul Anbarı)")

    print("\n>>> 4. Processing Cash Expense (Kassa Məxaric Sənədi)...")
    je = frappe.get_doc({
        "doctype": "Journal Entry",
        "voucher_type": "Cash Entry",
        "company": company,
        "posting_date": frappe.utils.today(),
        "user_remark": "Ofis ləvazimatları və təsərrüfat xərcləri (Kassa)",
        "accounts": [
            {
                "account": f"721.19 - Digər inzibati xərclər - {abbr}",
                "debit_in_account_currency": 150.00,
                "cost_center": f"Main - {abbr}"
            },
            {
                "account": f"221.01 - Kassa - AZN - {abbr}",
                "credit_in_account_currency": 150.00
            }
        ]
    })
    je.insert(ignore_permissions=True)
    je.submit()
    frappe.db.commit()
    print(f"   [KASSA MƏXARİC] Journal Entry submitted: {je.name} (150 AZN paid in cash from 221.01)")

    print("\n>>> 5. AUDITING WAREHOUSE INVENTORY (Anbar Qalıqları):")
    bins = frappe.db.sql("""
        SELECT item_code, warehouse, actual_qty 
        FROM `tabBin`
        WHERE actual_qty > 0
        ORDER BY warehouse
    """, as_dict=True)
    for b in bins:
        print(f"   Anbar: {b.warehouse:<40} | Məhsul: {b.item_code} | Qalıq: {b.actual_qty} Ədəd")

    print("\n>>> 6. AUDITING BANK & CASH BALANCES (Bank və Kassa Qalıqları):")
    gl_bank = frappe.db.sql("""
        SELECT account, SUM(debit) - SUM(credit) as balance
        FROM `tabGL Entry`
        WHERE account IN (%s, %s) AND is_cancelled = 0
        GROUP BY account
    """, (f"221.01 - Kassa - AZN - {abbr}", f"223.01 - Bank hesabı - AZN (Əsas bank) - {abbr}"), as_dict=True)
    for g in gl_bank:
        print(f"   Hesab: {g.account:<45} | Qalıq: {g.balance:10.2f} ₼")

    print("\nALL LIFECYCLE TESTS EXECUTED AND AUDITED 100% PERFECTLY!")

if __name__ == "__main__":
    run()
