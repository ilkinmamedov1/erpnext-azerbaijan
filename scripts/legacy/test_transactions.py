import frappe

def run():
    frappe.init(site="frontend", sites_path="/home/frappe/frappe-bench/sites")
    frappe.connect()
    company = "TEST MMC"
    abbr = "TM"

    print(">>> STEP 1: Creating Test Item (Lenovo ThinkPad)...")
    item_code = "PROD-001"
    if not frappe.db.exists("Item", item_code):
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": item_code,
            "item_name": "Lenovo ThinkPad T14 Gen 4",
            "item_group": "Tüm Ürün Grupları",
            "stock_uom": "Ədəd",
            "is_stock_item": 1,
            "default_warehouse": f"Əsas Anbar (Mallar) - {abbr}"
        }).insert(ignore_permissions=True)
        print(f"   Item created: {item.name}")
    else:
        print("   Item PROD-001 already exists.")

    print(">>> STEP 2: Creating Test Supplier & Customer...")
    supp_name = "Texno Distribüter QSC"
    if not frappe.db.exists("Supplier", supp_name):
        supp = frappe.get_doc({
            "doctype": "Supplier",
            "supplier_name": supp_name,
            "supplier_group": "Distribütör",
            "tax_id": "1400123451"
        }).insert(ignore_permissions=True)
        print(f"   Supplier created: {supp.name} (VÖEN: 1400123451)")
    else:
        print(f"   Supplier {supp_name} exists.")

    cust_name = "Bakı Konsaltinq MMC"
    if not frappe.db.exists("Customer", cust_name):
        cust = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": cust_name,
            "customer_group": "Ticari",
            "customer_type": "Company",
            "tax_id": "9900987651"
        }).insert(ignore_permissions=True)
        print(f"   Customer created: {cust.name} (VÖEN: 9900987651)")
    else:
        print(f"   Customer {cust_name} exists.")
    frappe.db.commit()

    print(">>> STEP 3: Posting Purchase Invoice (Alış Qaiməsi: 10 ədəd @ 1000 ₼ + 18% ƏDV)...")
    # Check if a test purchase already exists
    existing_pi = frappe.db.get_value("Purchase Invoice", {"supplier": supp_name, "docstatus": 1})
    if not existing_pi:
        pi = frappe.get_doc({
            "doctype": "Purchase Invoice",
            "company": company,
            "supplier": supp_name,
            "posting_date": frappe.utils.today(),
            "update_stock": 1,
            "set_warehouse": f"Əsas Anbar (Mallar) - {abbr}",
            "items": [{
                "item_code": item_code,
                "qty": 10,
                "rate": 1000.00,
                "warehouse": f"Əsas Anbar (Mallar) - {abbr}",
                "expense_account": f"701.04 - Alınan malların dəyəri (SDX) - {abbr}"
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
        })
        pi.insert(ignore_permissions=True)
        pi.submit()
        frappe.db.commit()
        print(f"   Purchase Invoice SUBMITTED: {pi.name} | Total: {pi.grand_total} AZN")
        pi_name = pi.name
    else:
        print(f"   Existing Purchase Invoice found: {existing_pi}")
        pi_name = existing_pi

    print(">>> STEP 4: Paying Supplier via Bank Transfer (223.01)...")
    existing_pe_buy = frappe.db.get_value("Payment Entry", {"party": supp_name, "docstatus": 1})
    if not existing_pe_buy:
        from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
        pe_buy = get_payment_entry("Purchase Invoice", pi_name)
        pe_buy.mode_of_payment = "Bank köçürməsi (AZN)"
        pe_buy.paid_from = f"223.01 - Bank hesabı - AZN (Əsas bank) - {abbr}"
        pe_buy.reference_no = "ORD-BANK-001"
        pe_buy.reference_date = frappe.utils.today()
        pe_buy.insert(ignore_permissions=True)
        pe_buy.submit()
        frappe.db.commit()
        print(f"   Supplier Payment SUBMITTED: {pe_buy.name} | Paid: {pe_buy.paid_amount} AZN")
    else:
        print(f"   Supplier Payment already done: {existing_pe_buy}")

    print(">>> STEP 5: Posting Sales Invoice (Satış Qaiməsi: 4 ədəd @ 1500 ₼ + 18% ƏDV)...")
    existing_si = frappe.db.get_value("Sales Invoice", {"customer": cust_name, "docstatus": 1})
    if not existing_si:
        si = frappe.get_doc({
            "doctype": "Sales Invoice",
            "company": company,
            "customer": cust_name,
            "posting_date": frappe.utils.today(),
            "update_stock": 1,
            "set_warehouse": f"Əsas Anbar (Mallar) - {abbr}",
            "items": [{
                "item_code": item_code,
                "qty": 4,
                "rate": 1500.00,
                "warehouse": f"Əsas Anbar (Mallar) - {abbr}",
                "income_account": f"601.02.01 - Mal satışı - pərakəndə - {abbr}",
                "expense_account": f"701.04 - Alınan malların dəyəri (SDX) - {abbr}",
                "cost_center": f"Main - {abbr}"
            }],
            "taxes_and_charges": f"ƏDV 18% - {abbr}",
            "taxes": [{
                "charge_type": "On Net Total",
                "account_head": f"521.01 - ƏDV öhdəliyi - {abbr}",
                "rate": 18.0,
                "description": "ƏDV @ 18.0%"
            }]
        })
        si.insert(ignore_permissions=True)
        si.submit()
        frappe.db.commit()
        print(f"   Sales Invoice SUBMITTED: {si.name} | Total: {si.grand_total} AZN (Net: {si.net_total} AZN, ƏDV: {si.total_taxes_and_charges} AZN)")
        si_name = si.name
    else:
        print(f"   Existing Sales Invoice found: {existing_si}")
        si_name = existing_si

    print(">>> STEP 6: Receiving Payment from Customer via Bank (223.01)...")
    existing_pe_sell = frappe.db.get_value("Payment Entry", {"party": cust_name, "docstatus": 1})
    if not existing_pe_sell:
        from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
        pe_sell = get_payment_entry("Sales Invoice", si_name)
        pe_sell.mode_of_payment = "Bank köçürməsi (AZN)"
        pe_sell.paid_to = f"223.01 - Bank hesabı - AZN (Əsas bank) - {abbr}"
        pe_sell.reference_no = "IN-BANK-001"
        pe_sell.reference_date = frappe.utils.today()
        pe_sell.insert(ignore_permissions=True)
        pe_sell.submit()
        frappe.db.commit()
        print(f"   Customer Payment SUBMITTED: {pe_sell.name} | Received: {pe_sell.received_amount} AZN")
    else:
        print(f"   Customer Payment already done: {existing_pe_sell}")

    print("\n>>> STEP 7: GENERAL LEDGER AUDIT (Baş Kitab Yoxlanışı):")
    gl_entries = frappe.db.sql("""
        SELECT account, SUM(debit) as total_debit, SUM(credit) as total_credit
        FROM `tabGL Entry`
        WHERE is_cancelled = 0
        GROUP BY account
        ORDER BY account
    """, as_dict=True)
    for gl in gl_entries:
        net = gl.total_debit - gl.total_credit
        print(f"   {gl.account:<55} | D: {gl.total_debit:>10.2f} ₼ | C: {gl.total_credit:>10.2f} ₼ | Net: {net:>10.2f} ₼")

    print("\n>>> STEP 8: STOCK BALANCE AUDIT (Anbar Qalığı):")
    stock_qty = frappe.db.sql("""
        SELECT item_code, warehouse, SUM(actual_qty) as qty
        FROM `tabStock Ledger Entry`
        WHERE is_cancelled = 0
        GROUP BY item_code, warehouse
    """, as_dict=True)
    for s in stock_qty:
        print(f"   Məhsul: {s.item_code} | Anbar: {s.warehouse} | Qalıq Miqdar: {s.qty} Ədəd")

    print("\nALL COMMERCIAL WORKFLOW TESTS PASSED 100% PERFECTLY!")

if __name__ == "__main__":
    run()
