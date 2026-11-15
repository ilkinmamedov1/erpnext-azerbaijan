#!/usr/bin/env python3
"""
ERPNext Azerbaijan Localized Initialization Script
Automates:
1. Currency AZN activation
2. Non-interactive Setup Wizard completion (if not completed)
3. 427 Azerbaijani Standard Chart of Accounts (Hesablar Planı) Import & Tree Build
4. Company default account mappings (Kassa, Bank, Alıcılar, Malsatanlar, Mallar, SDX, ƏDV)
5. Tax templates (ƏDV 18%, 0%, Azad, Əvəzləşdirilən)
6. Warehouses (Bütün Anbarlar, Əsas Anbar, Hazır Məhsul, Xammal, Bitməmiş İstehsalat, Tranzit)
7. Modes of Payment (Nağd, Bank köçürməsi, POS-Terminal, ƏDV Depozit)
8. Bank and Bank Account (Configurable from .env or defaults)
9. Units of Measure (Ədəd, Qutu, Dəst, Paçka, Rulon, Qram, Ton)
10. Property Setters (VÖEN label & Naming Series SQ-, AQ-, SS-, AS-, TQ-, MQ-, ÖD-, MƏ-)
11. Central Bank (CBAR) reference exchange rates
12. Official Azerbaijani "Hesab-Faktura (Azərbaycan)" Print Format
13. Azerbaijani UI Translations
"""

import os
import sys
import csv
import frappe
from frappe.utils.nestedset import rebuild_tree
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def run():
    site_name = os.environ.get("SITE_NAME", "frontend")
    company_name = os.environ.get("COMPANY_NAME", "TEST MMC")
    company_abbr = os.environ.get("COMPANY_ABBR", "TM")
    company_tax_id = os.environ.get("COMPANY_TAX_ID", "1300000001")
    bank_name = os.environ.get("BANK_NAME", "Bank Hesabı") or "Bank Hesabı"
    bank_swift = os.environ.get("BANK_SWIFT", "") or ""
    bank_iban = os.environ.get("BANK_IBAN", "") or ""
    
    # Locate CSV file
    csv_candidates = [
        os.environ.get("COA_CSV_PATH", ""),
        "/data/azerbaijan_coa.csv",
        "/home/frappe/frappe-bench/sites/azerbaijan_coa.csv",
        os.path.join(os.path.dirname(__file__), "..", "data", "azerbaijan_coa.csv"),
        os.path.join(os.path.dirname(__file__), "azerbaijan_coa.csv"),
    ]
    csv_path = None
    for cand in csv_candidates:
        if cand and os.path.exists(cand):
            csv_path = os.path.abspath(cand)
            break
            
    if not csv_path:
        raise FileNotFoundError(f"Could not locate azerbaijan_coa.csv in candidates: {csv_candidates}")

    # Ensure logs directory accessible from any cwd
    bench_logs = "/home/frappe/frappe-bench/logs"
    if os.path.exists(bench_logs) and not os.path.exists("/home/frappe/logs"):
        try:
            os.symlink(bench_logs, "/home/frappe/logs")
        except Exception:
            pass

    print(f"=== INITIALIZING AZERBAIJAN LOCALIZATION FOR {company_name} ({company_abbr}) ===")
    print(f"Using Chart of Accounts CSV: {csv_path}")

    frappe.init(site=site_name, sites_path="/home/frappe/frappe-bench/sites")
    frappe.connect()
    frappe.set_user("Administrator")

    # 1. Enable / Create AZN in Currency DocType
    print("\n>>> 1. Ensuring AZN currency is created and enabled in Frappe...")
    if not frappe.db.exists("Currency", "AZN"):
        frappe.get_doc({
            "doctype": "Currency",
            "currency_name": "AZN",
            "enabled": 1,
            "fraction": "Qəpik",
            "fraction_units": 100,
            "smallest_currency_fraction_value": 0.01,
            "symbol": "₼",
            "symbol_on_right": 1,
            "number_format": "#,###.##"
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        print("   Currency AZN created and enabled successfully!")
    else:
        frappe.db.set_value("Currency", "AZN", "enabled", 1)
        frappe.db.commit()
        print("   Currency AZN enabled successfully!")

    # 2. Check and Complete Setup Wizard if needed
    print("\n>>> 2. Checking Setup Wizard status...")
    if not frappe.is_setup_complete():
        print("   Setup wizard is not yet complete. Running non-interactive setup wizard...")
        current_year = frappe.utils.today().split("-")[0]
        wizard_args = {
            "language": "en",
            "country": "Azerbaijan",
            "timezone": "Asia/Baku",
            "currency": "AZN",
            "company_name": company_name,
            "company_abbr": company_abbr,
            "domain": "Distribution",
            "fy_start_date": f"{current_year}-01-01",
            "fy_end_date": f"{current_year}-12-31",
            "full_name": "Administrator",
            "email": "admin@example.com",
            "chart_of_accounts": "Standard",
        }
        from frappe.desk.page.setup_wizard.setup_wizard import setup_complete
        setup_complete(wizard_args)
        frappe.db.commit()
        print("   Setup wizard completed successfully!")
    else:
        print("   Setup wizard already marked complete.")

    # Ensure company exists
    if not frappe.db.exists("Company", company_name):
        print(f"   Creating Company {company_name}...")
        comp = frappe.get_doc({
            "doctype": "Company",
            "company_name": company_name,
            "abbr": company_abbr,
            "default_currency": "AZN",
            "country": "Azerbaijan"
        }).insert(ignore_permissions=True)
        frappe.db.commit()

    abbr = frappe.db.get_value("Company", company_name, "abbr") or company_abbr

    # 3. Import Azerbaijani Chart of Accounts (427 accounts)
    print("\n>>> 3. Checking Azerbaijani Chart of Accounts (CoA)...")
    az_root_exists = frappe.db.exists("Account", f"1 - UZUNMÜDDƏTLİ AKTİVLƏR - {abbr}")
    if not az_root_exists:
        print(f"   Importing 427 Azerbaijani accounts into {company_name}...")

        # Clear existing mode of payment account links for company
        frappe.db.sql("DELETE FROM `tabMode of Payment Account` WHERE company = %s", (company_name,))

        # Clear default accounts in Company
        frappe.db.sql("""
            UPDATE `tabCompany` SET
                default_cash_account = NULL,
                default_bank_account = NULL,
                default_receivable_account = NULL,
                default_payable_account = NULL,
                stock_received_but_not_billed = NULL,
                stock_adjustment_account = NULL,
                default_inventory_account = NULL,
                default_income_account = NULL,
                default_expense_account = NULL,
                round_off_account = NULL,
                write_off_account = NULL,
                default_discount_account = NULL,
                exchange_gain_loss_account = NULL,
                unrealized_exchange_gain_loss_account = NULL,
                expenses_included_in_asset_valuation = NULL,
                expenses_included_in_valuation = NULL
            WHERE name = %s
        """, (company_name,))

        # Wipe placeholder accounts
        old_accounts = frappe.db.get_all("Account", filters={"company": company_name}, pluck="name")
        print(f"   Removing {len(old_accounts)} temporary accounts created by setup wizard...")
        frappe.db.sql("DELETE FROM `tabAccount` WHERE company = %s", (company_name,))
        frappe.db.commit()

        # Read CSV
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        num_to_row = {}
        for r in rows:
            num = r["Account Number"].strip()
            num_to_row[num] = r

        id_map = {}
        for num, r in num_to_row.items():
            name = r["Account Name"].strip()
            full_id = f"{num} - {name} - {abbr}"
            id_map[num] = full_id

        # Insert topologically
        created = set()
        to_create = list(num_to_row.keys())
        inserted_count = 0
        frappe.flags.allow_unverified_charts = True

        while to_create:
            progress = False
            remaining = []
            for num in to_create:
                r = num_to_row[num]
                p_num = r["Parent Account Number"].strip()

                if not p_num or p_num in created:
                    acct_name = r["Account Name"].strip()
                    full_id = id_map[num]
                    parent_id = id_map[p_num] if p_num else None
                    is_group = int(r["Is Group"].strip())
                    root_type = r["Root Type"].strip()
                    report_type = r["Report Type"].strip()
                    currency = r["Account Currency"].strip() or "AZN"
                    acct_type = r["Account Type"].strip() or None

                    if num in ["241", "241.01", "241.02", "521", "521.01"]:
                        if not acct_type:
                            acct_type = "Tax"
                    elif num.startswith("112"):
                        acct_type = "Accumulated Depreciation"
                    elif num == "113":
                        acct_type = "Capital Work in Progress"

                    doc = frappe.new_doc("Account")
                    doc.name = full_id
                    doc.account_number = num
                    doc.account_name = acct_name
                    doc.company = company_name
                    doc.parent_account = parent_id
                    doc.is_group = is_group
                    doc.root_type = root_type
                    doc.report_type = report_type
                    doc.account_currency = currency
                    if acct_type:
                        doc.account_type = acct_type

                    doc.flags.ignore_validate = True
                    doc.flags.ignore_mandatory = True
                    doc.flags.ignore_permissions = True
                    doc.insert()

                    created.add(num)
                    inserted_count += 1
                    progress = True
                else:
                    remaining.append(num)

            if not progress:
                print(f"Cycle detected or unresolvable parents for: {remaining}")
                break
            to_create = remaining

        print(f"   Successfully inserted {inserted_count} accounts from CSV!")

        # Add Stock Received But Not Billed helper under 531
        srbnb_id = f"531.05 - Fakturası daxil olmamış mallar üzrə borclar - {abbr}"
        if not frappe.db.exists("Account", srbnb_id):
            srbnb = frappe.new_doc("Account")
            srbnb.name = srbnb_id
            srbnb.account_number = "531.05"
            srbnb.account_name = "Fakturası daxil olmamış mallar üzrə borclar"
            srbnb.company = company_name
            srbnb.parent_account = id_map.get("531", f"531 - Malsatanlara qısamüddətli kreditor borcları - {abbr}")
            srbnb.is_group = 0
            srbnb.root_type = "Liability"
            srbnb.report_type = "Balance Sheet"
            srbnb.account_currency = "AZN"
            srbnb.account_type = "Stock Received But Not Billed"
            srbnb.flags.ignore_validate = True
            srbnb.insert()
            print(f"   Created helper account: {srbnb_id}")

        # Rebuild nested set tree
        print("   Rebuilding nested set account tree...")
        rebuild_tree("Account", "parent_account")

        # Link default company accounts
        def get_id(num, default=None):
            return id_map.get(num, default)

        cash_acct = get_id("221.01")     # Kassa - AZN
        bank_acct = get_id("223.01")     # Bank hesabı - AZN (Əsas bank)
        recv_acct = get_id("211.01.01")  # Yerli alıcılar - hüquqi şəxslər
        pay_acct = get_id("531.01.01")   # Yerli malsatanlar - hüquqi şəxslər
        stock_acct = get_id("205.01")    # Mallar - anbar
        income_acct = get_id("601.02.01")# Mal satışı - pərakəndə
        expense_acct = get_id("701.04")  # Alınan malların dəyəri (SDX)
        stock_adj = get_id("208")        # Ehtiyatların dəyər düzəlişi
        round_off = get_id("721.19")     # Digər inzibati xərclər
        ex_gain_loss = get_id("631.04")  # Valyuta məzənnə fərqi (mənfəət)

        frappe.db.set_value("Company", company_name, {
            "default_cash_account": cash_acct,
            "default_bank_account": bank_acct,
            "default_receivable_account": recv_acct,
            "default_payable_account": pay_acct,
            "default_inventory_account": stock_acct,
            "default_income_account": income_acct,
            "default_expense_account": expense_acct,
            "stock_adjustment_account": stock_adj,
            "stock_received_but_not_billed": srbnb_id,
            "round_off_account": round_off,
            "exchange_gain_loss_account": ex_gain_loss
        })
        frappe.db.commit()
        print("   Company default accounts successfully linked to Azerbaijani CoA!")
    else:
        print("   Azerbaijani Chart of Accounts is already installed and verified.")

    # 4. Configure Company Details & Asset Accounts
    print("\n>>> 4. Configuring Company Details & Fixed Assets accounts...")
    acct_112_06 = f"112.06 - Digər TTA üzrə amortizasiya - {abbr}"
    acct_113 = f"113 - TTA ilə bağlı məsrəflərin kapitallaşdırılması - {abbr}"
    if frappe.db.exists("Account", acct_112_06):
        frappe.db.set_value("Account", acct_112_06, "account_type", "Accumulated Depreciation")
    if frappe.db.exists("Account", acct_113):
        frappe.db.set_value("Account", acct_113, "account_type", "Capital Work in Progress")
    frappe.db.commit()

    comp = frappe.get_doc("Company", company_name)
    comp.tax_id = company_tax_id
    comp.default_currency = "AZN"
    comp.accumulated_depreciation_account = f"112.06 - Digər TTA üzrə amortizasiya - {abbr}"
    comp.depreciation_expense_account = f"721.08 - TTA amortizasiyası (inzibati) - {abbr}"
    comp.capital_work_in_progress_account = f"113 - TTA ilə bağlı məsrəflərin kapitallaşdırılması - {abbr}"
    comp.disposal_account = f"731.04 - Aktivlərin silinməsi zərərləri - {abbr}"
    comp.asset_received_but_not_billed = None
    comp.expenses_included_in_asset_valuation = None
    comp.expenses_included_in_valuation = None
    comp.save()
    frappe.db.commit()
    print(f"   Company VÖEN set to {company_tax_id} and Asset accounts mapped.")

    # 5. Configure Bank & Bank Account
    print("\n>>> 5. Configuring Bank and Bank Account...")
    if not frappe.db.exists("Bank", bank_name):
        frappe.get_doc({
            "doctype": "Bank",
            "bank_name": bank_name,
            "swift_number": bank_swift
        }).insert(ignore_permissions=True)
    
    bank_account_title = f"{bank_name} Əsas Hesab"
    existing_ba = frappe.db.get_value("Bank Account", {"company": company_name, "bank": bank_name}, "name")
    if not existing_ba:
        frappe.get_doc({
            "doctype": "Bank Account",
            "account_name": bank_account_title,
            "bank": bank_name,
            "account": f"223.01 - Bank hesabı - AZN (Əsas bank) - {abbr}",
            "company": company_name,
            "is_company_account": 1,
            "is_default": 1,
            "iban": bank_iban
        }).insert(ignore_permissions=True)
    frappe.db.commit()
    print(f"   Bank {bank_name} and IBAN {bank_iban} linked to 223.01.")

    # 6. Configure Tax Templates (ƏDV 18%, 0%, Əvəzləşdirilən)
    print("\n>>> 6. Configuring Azerbaijani Tax Templates...")
    # Sales Tax: ƏDV 18%
    sales_tax_18 = f"ƏDV 18% - {abbr}"
    if not frappe.db.exists("Sales Taxes and Charges Template", sales_tax_18):
        frappe.get_doc({
            "doctype": "Sales Taxes and Charges Template",
            "title": "ƏDV 18%",
            "company": company_name,
            "is_default": 1,
            "taxes": [{
                "charge_type": "On Net Total",
                "account_head": f"521.01 - ƏDV öhdəliyi - {abbr}",
                "rate": 18.0,
                "description": "ƏDV @ 18.0%"
            }]
        }).insert(ignore_permissions=True)

    # Sales Tax: ƏDV 0% (İxrac)
    sales_tax_0 = f"ƏDV 0% (İxrac) - {abbr}"
    if not frappe.db.exists("Sales Taxes and Charges Template", sales_tax_0):
        frappe.get_doc({
            "doctype": "Sales Taxes and Charges Template",
            "title": "ƏDV 0% (İxrac)",
            "company": company_name,
            "is_default": 0,
            "taxes": [{
                "charge_type": "On Net Total",
                "account_head": f"521.01 - ƏDV öhdəliyi - {abbr}",
                "rate": 0.0,
                "description": "ƏDV @ 0%"
            }]
        }).insert(ignore_permissions=True)

    # Sales Tax: ƏDV-dən Azad
    sales_tax_exempt = f"ƏDV-dən Azad - {abbr}"
    if not frappe.db.exists("Sales Taxes and Charges Template", sales_tax_exempt):
        frappe.get_doc({
            "doctype": "Sales Taxes and Charges Template",
            "title": "ƏDV-dən Azad",
            "company": company_name,
            "is_default": 0,
            "taxes": [{
                "charge_type": "On Net Total",
                "account_head": f"521.01 - ƏDV öhdəliyi - {abbr}",
                "rate": 0.0,
                "description": "ƏDV-dən azad"
            }]
        }).insert(ignore_permissions=True)

    # Purchase Tax: ƏDV 18% (Yerli alışlar)
    purch_tax_18 = f"ƏDV 18% (Yerli alışlar) - {abbr}"
    if not frappe.db.exists("Purchase Taxes and Charges Template", purch_tax_18):
        frappe.get_doc({
            "doctype": "Purchase Taxes and Charges Template",
            "title": "ƏDV 18% (Yerli alışlar)",
            "company": company_name,
            "is_default": 1,
            "taxes": [{
                "charge_type": "On Net Total",
                "account_head": f"241.01 - ƏDV əvəzləşməsi - yerli alışlar - {abbr}",
                "rate": 18.0,
                "description": "ƏDV @ 18% (Əvəzləşdirilən)",
                "category": "Valuation and Total",
                "add_deduct_tax": "Add"
            }]
        }).insert(ignore_permissions=True)

    # Purchase Tax: ƏDV 18% (İdxal)
    purch_tax_import = f"ƏDV 18% (İdxal) - {abbr}"
    if not frappe.db.exists("Purchase Taxes and Charges Template", purch_tax_import):
        frappe.get_doc({
            "doctype": "Purchase Taxes and Charges Template",
            "title": "ƏDV 18% (İdxal)",
            "company": company_name,
            "is_default": 0,
            "taxes": [{
                "charge_type": "On Net Total",
                "account_head": f"241.02 - ƏDV əvəzləşməsi - idxal - {abbr}",
                "rate": 18.0,
                "description": "ƏDV @ 18% (İdxal)",
                "category": "Valuation and Total",
                "add_deduct_tax": "Add"
            }]
        }).insert(ignore_permissions=True)
    frappe.db.commit()
    print("   Sales & Purchase Tax templates created.")

    # 7. Configure Modes of Payment
    print("\n>>> 7. Configuring Modes of Payment...")
    payment_modes = [
        ("Nağd (Kassa)", "Cash", f"221.01 - Kassa - AZN - {abbr}"),
        ("Bank köçürməsi (AZN)", "Bank", f"223.01 - Bank hesabı - AZN (Əsas bank) - {abbr}"),
        ("POS-Terminal / Kart", "Bank", f"223.01 - Bank hesabı - AZN (Əsas bank) - {abbr}"),
        ("ƏDV Depozit Hesabı", "Bank", f"226 - ƏDV sub-uçot hesabı - {abbr}")
    ]
    for mode_name, mode_type, account_name in payment_modes:
        if not frappe.db.exists("Mode of Payment", mode_name):
            frappe.get_doc({
                "doctype": "Mode of Payment",
                "mode_of_payment": mode_name,
                "type": mode_type,
                "enabled": 1,
                "accounts": [{
                    "company": company_name,
                    "default_account": account_name
                }]
            }).insert(ignore_permissions=True)
        else:
            doc = frappe.get_doc("Mode of Payment", mode_name)
            doc.type = mode_type
            doc.enabled = 1
            found = False
            for row in doc.accounts:
                if row.company == company_name:
                    row.default_account = account_name
                    found = True
            if not found:
                doc.append("accounts", {
                    "company": company_name,
                    "default_account": account_name
                })
            doc.save()

    for old_mode in ["Kontrol etmek", "Kredi Kartı", "Elektronik Transfer", "Banka Havalesi", "Nakit", "Cash", "Cheque"]:
        if frappe.db.exists("Mode of Payment", old_mode):
            m = frappe.get_doc("Mode of Payment", old_mode)
            m.enabled = 0
            m.save()
    frappe.db.commit()
    print("   Modes of Payment active and cleanly linked.")

    # 8. Configure Warehouses
    print("\n>>> 8. Configuring Warehouses...")
    wh_renames = [
        (f"Tüm Depolar - {abbr}", f"Bütün Anbarlar - {abbr}", 1, None),
        (f"Mağazalar - {abbr}", f"Əsas Anbar (Mallar) - {abbr}", 0, f"205.01 - Mallar - anbar - {abbr}"),
        (f"Mamüller - {abbr}", f"Hazır Məhsul Anbarı - {abbr}", 0, f"204.01 - Hazır məhsul - anbar 1 - {abbr}"),
        (f"Devam ediyor - {abbr}", f"Bitməmiş İstehsalat Anbarı - {abbr}", 0, f"202.01 - Bitməmiş istehsalat - əsas - {abbr}"),
        (f"Transit Ürünler - {abbr}", f"Tranzit Anbar (Yolda olan mallar) - {abbr}", 0, f"207 - Digər ehtiyatlar - {abbr}"),
        (f"All Warehouses - {abbr}", f"Bütün Anbarlar - {abbr}", 1, None),
        (f"Stores - {abbr}", f"Əsas Anbar (Mallar) - {abbr}", 0, f"205.01 - Mallar - anbar - {abbr}"),
        (f"Finished Goods - {abbr}", f"Hazır Məhsul Anbarı - {abbr}", 0, f"204.01 - Hazır məhsul - anbar 1 - {abbr}"),
        (f"Work In Progress - {abbr}", f"Bitməmiş İstehsalat Anbarı - {abbr}", 0, f"202.01 - Bitməmiş istehsalat - əsas - {abbr}"),
    ]
    for old_wh, new_wh, is_grp, acc in wh_renames:
        if frappe.db.exists("Warehouse", old_wh):
            frappe.rename_doc("Warehouse", old_wh, new_wh, force=True)
        if frappe.db.exists("Warehouse", new_wh):
            w = frappe.get_doc("Warehouse", new_wh)
            if acc:
                w.account = acc
            w.save()

    mat_wh = f"Xammal və Materiallar Anbarı - {abbr}"
    if not frappe.db.exists("Warehouse", mat_wh):
        frappe.get_doc({
            "doctype": "Warehouse",
            "warehouse_name": "Xammal və Materiallar Anbarı",
            "is_group": 0,
            "parent_warehouse": f"Bütün Anbarlar - {abbr}",
            "company": company_name,
            "account": f"201.01.01 - Xammal - yerli - {abbr}"
        }).insert(ignore_permissions=True)

    if frappe.db.exists("Warehouse", f"Əsas Anbar (Mallar) - {abbr}"):
        stock_settings = frappe.get_doc("Stock Settings")
        stock_settings.default_warehouse = f"Əsas Anbar (Mallar) - {abbr}"
        stock_settings.save()
    frappe.db.commit()
    print("   Warehouses restructured with Azerbaijani nomenclature.")

    # 9. Configure Units of Measure (UOM)
    print("\n>>> 9. Configuring Units of Measure (UOM)...")
    uoms = [
        ("Ədəd", 0),
        ("Qutu", 0),
        ("Dəst", 0),
        ("Paçka", 0),
        ("Rulon", 0),
        ("Qram", 1),
        ("Ton", 1)
    ]
    for uom_name, must_be_whole_number in uoms:
        if not frappe.db.exists("UOM", uom_name):
            frappe.get_doc({
                "doctype": "UOM",
                "uom_name": uom_name,
                "must_be_whole_number": 0 if must_be_whole_number else 1,
                "enabled": 1
            }).insert(ignore_permissions=True)
    frappe.db.commit()
    print("   Azerbaijani UOMs registered.")

    # 10. Configure Property Setters (VÖEN label & Naming Series)
    print("\n>>> 10. Configuring VÖEN labels and Azerbaijani Naming Series...")
    for dt in ["Company", "Customer", "Supplier"]:
        make_property_setter(dt, "tax_id", "label", "VÖEN", "Data", for_doctype=False)
        frappe.db.commit()

    series_map = {
        "Sales Invoice": ("SQ-.YYYY.-.#####\nSQ-RET-.YYYY.-.#####", "SQ-.YYYY.-.#####"),
        "Purchase Invoice": ("AQ-.YYYY.-.#####\nAQ-RET-.YYYY.-.#####", "AQ-.YYYY.-.#####"),
        "Sales Order": ("SS-.YYYY.-.#####", "SS-.YYYY.-.#####"),
        "Purchase Order": ("AS-.YYYY.-.#####", "AS-.YYYY.-.#####"),
        "Delivery Note": ("TQ-.YYYY.-.#####", "TQ-.YYYY.-.#####"),
        "Purchase Receipt": ("MQ-.YYYY.-.#####", "MQ-.YYYY.-.#####"),
        "Payment Entry": ("ÖD-.YYYY.-.#####", "ÖD-.YYYY.-.#####"),
        "Journal Entry": ("MƏ-.YYYY.-.#####", "MƏ-.YYYY.-.#####")
    }
    for dt, (opts, dflt) in series_map.items():
        if frappe.db.exists("DocType", dt):
            make_property_setter(dt, "naming_series", "options", opts, "Text", for_doctype=False)
            make_property_setter(dt, "naming_series", "default", dflt, "Text", for_doctype=False)
    frappe.db.commit()
    print("   VÖEN labels and Naming Series (SQ-, AQ-, SS-, AS-, TQ-, MQ-, ÖD-, MƏ-) set.")

    # 11. Central Bank Exchange Rates (CBAR reference)
    print("\n>>> 11. Setting Central Bank (CBAR) reference exchange rates...")
    rates = [
        ("USD", "AZN", 1.7000),
        ("EUR", "AZN", 1.8450),
        ("RUB", "AZN", 0.0175),
        ("TRY", "AZN", 0.0495),
        ("GBP", "AZN", 2.2100)
    ]
    for from_cur, to_cur, rate in rates:
        existing = frappe.db.get_value("Currency Exchange", {
            "from_currency": from_cur,
            "to_currency": to_cur,
            "date": frappe.utils.today()
        })
        if not existing:
            frappe.get_doc({
                "doctype": "Currency Exchange",
                "date": frappe.utils.today(),
                "from_currency": from_cur,
                "to_currency": to_cur,
                "exchange_rate": rate,
                "for_buying": 1,
                "for_selling": 1
            }).insert(ignore_permissions=True)
    frappe.db.commit()
    print("   CBAR benchmark rates initialized.")

    # 12. Azerbaijani Hesab-Faktura Print Format
    print("\n>>> 12. Registering Hesab-Faktura (Azərbaycan) Print Format...")
    pf_name = "Hesab-Faktura (Azərbaycan)"
    if frappe.db.exists("Print Format", pf_name):
        frappe.delete_doc("Print Format", pf_name, force=True)

    html_template = """
<div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1e293b; padding: 25px; font-size: 13px; line-height: 1.5;">
    <!-- HEADER -->
    <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #0f766e; padding-bottom: 15px; margin-bottom: 20px;">
        <div style="width: 55%;">
            <h2 style="margin: 0; color: #0f766e; font-size: 22px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">{{ doc.company }}</h2>
            <div style="margin-top: 5px; color: #475569; font-size: 12px;">
                <div><strong>VÖEN:</strong> {{ frappe.db.get_value("Company", doc.company, "tax_id") or "1300000001" }}</div>
                <div><strong>Ünvan:</strong> Bakı şəhəri, Nizami r-nu, Nizami küç. 120</div>
                <div><strong>Valyuta:</strong> {{ doc.currency }} (AZN - ₼)</div>
            </div>
        </div>
        <div style="width: 42%; text-align: right; background: #f8fafc; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0;">
            <div style="font-size: 16px; font-weight: 700; color: #0f766e; margin-bottom: 4px;">HESAB-FAKTURA</div>
            <div style="font-size: 13px; font-weight: 600; color: #1e293b;">№ {{ doc.name }}</div>
            <div style="font-size: 12px; color: #64748b; margin-top: 4px;">Tarix: <strong>{{ frappe.utils.formatdate(doc.posting_date) }}</strong></div>
            {% if doc.due_date %}
            <div style="font-size: 12px; color: #64748b;">Son ödəniş tarixi: {{ frappe.utils.formatdate(doc.due_date) }}</div>
            {% endif %}
        </div>
    </div>

    <!-- BANK REKVİZİTLƏRİ VƏ ALICI -->
    <div style="display: flex; justify-content: space-between; margin-bottom: 20px; gap: 20px;">
        <div style="flex: 1; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px;">
            <div style="font-weight: 700; color: #0f766e; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; margin-bottom: 8px; font-size: 12px; text-transform: uppercase;">Bank Rekvizitləri</div>
            <div style="font-size: 12px; line-height: 1.6;">
                {% set ba = frappe.db.get_value("Bank Account", {"company": doc.company, "is_default": 1}, ["bank", "iban"], as_dict=True) %}
                <div><strong>Bank:</strong> {{ ba.bank if ba and ba.bank else "Bank Hesabı" }}</div>
                {% if ba and ba.iban %}
                <div><strong>İBAN:</strong> {{ ba.iban }}</div>
                {% endif %}
                <div><strong>Hesablaşma hesabı:</strong> 223.01</div>
            </div>
        </div>
        <div style="flex: 1; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px;">
            <div style="font-weight: 700; color: #0f766e; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; margin-bottom: 8px; font-size: 12px; text-transform: uppercase;">Alıcı Təşkilat</div>
            <div style="font-size: 12px; line-height: 1.6;">
                <div><strong>Müştəri:</strong> {{ doc.customer_name }}</div>
                <div><strong>VÖEN:</strong> {{ frappe.db.get_value("Customer", doc.customer, "tax_id") or "—" }}</div>
                <div><strong>Əlaqə:</strong> {{ doc.contact_display or "—" }}</div>
            </div>
        </div>
    </div>

    <!-- MƏHSUL VƏ XİDMƏTLƏR CƏDVƏLİ -->
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 12px;">
        <thead>
            <tr style="background: #0f766e; color: #ffffff;">
                <th style="padding: 10px; border: 1px solid #0f766e; text-align: center; width: 5%;">№</th>
                <th style="padding: 10px; border: 1px solid #0f766e; text-align: left; width: 45%;">Malın / Xidmətin Adı</th>
                <th style="padding: 10px; border: 1px solid #0f766e; text-align: center; width: 10%;">Ölçü</th>
                <th style="padding: 10px; border: 1px solid #0f766e; text-align: right; width: 10%;">Miqdar</th>
                <th style="padding: 10px; border: 1px solid #0f766e; text-align: right; width: 15%;">Qiymət (₼)</th>
                <th style="padding: 10px; border: 1px solid #0f766e; text-align: right; width: 15%;">Məbləğ (₼)</th>
            </tr>
        </thead>
        <tbody>
            {% for item in doc.items %}
            <tr style="background: {{ '#f8fafc' if loop.index % 2 == 0 else '#ffffff' }};">
                <td style="padding: 9px; border: 1px solid #cbd5e1; text-align: center;">{{ loop.index }}</td>
                <td style="padding: 9px; border: 1px solid #cbd5e1; font-weight: 500;">{{ item.item_name }}</td>
                <td style="padding: 9px; border: 1px solid #cbd5e1; text-align: center;">{{ item.uom }}</td>
                <td style="padding: 9px; border: 1px solid #cbd5e1; text-align: right;">{{ item.qty }}</td>
                <td style="padding: 9px; border: 1px solid #cbd5e1; text-align: right;">{{ frappe.format_value(item.rate, {"fieldtype": "Currency", "currency": doc.currency}) }}</td>
                <td style="padding: 9px; border: 1px solid #cbd5e1; text-align: right; font-weight: 600;">{{ frappe.format_value(item.amount, {"fieldtype": "Currency", "currency": doc.currency}) }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <!-- YEKUNLAR VƏ ƏDV -->
    <div style="display: flex; justify-content: flex-end; margin-bottom: 25px;">
        <table style="width: 45%; border-collapse: collapse; font-size: 13px;">
            <tr>
                <td style="padding: 6px 12px; text-align: right; color: #64748b;">Xalis Məbləğ (ƏDV-siz):</td>
                <td style="padding: 6px 12px; text-align: right; font-weight: 600; width: 45%;">{{ frappe.format_value(doc.net_total, {"fieldtype": "Currency", "currency": doc.currency}) }}</td>
            </tr>
            {% for tax in doc.taxes %}
            <tr>
                <td style="padding: 6px 12px; text-align: right; color: #64748b;">{{ tax.description }}:</td>
                <td style="padding: 6px 12px; text-align: right; font-weight: 600;">{{ frappe.format_value(tax.tax_amount, {"fieldtype": "Currency", "currency": doc.currency}) }}</td>
            </tr>
            {% endfor %}
            <tr style="border-top: 2px solid #0f766e; background: #f0fdfa;">
                <td style="padding: 10px 12px; text-align: right; font-weight: 700; color: #0f766e; font-size: 14px;">Yekun Ödəniləcək:</td>
                <td style="padding: 10px 12px; text-align: right; font-weight: 700; color: #0f766e; font-size: 15px;">{{ frappe.format_value(doc.grand_total, {"fieldtype": "Currency", "currency": doc.currency}) }}</td>
            </tr>
        </table>
    </div>

    <!-- MƏBLƏĞ SÖZLƏ -->
    <div style="background: #f8fafc; border-left: 4px solid #0f766e; padding: 10px 15px; margin-bottom: 35px; border-radius: 0 4px 4px 0; font-size: 12px;">
        <strong>Məbləğ sözlə:</strong> {{ doc.in_words or "" }}
    </div>

    <!-- İMZALAR VƏ MÖHÜR -->
    <div style="display: flex; justify-content: space-between; margin-top: 40px; padding-top: 20px; border-top: 1px dashed #cbd5e1;">
        <div style="width: 40%;">
            <div style="margin-bottom: 40px;"><strong>Direktor:</strong> ______________________</div>
            <div><strong>Baş Mühasib:</strong> ______________________</div>
        </div>
        <div style="width: 25%; text-align: center; display: flex; align-items: center; justify-content: center; border: 1px dashed #94a3b8; border-radius: 50%; width: 90px; height: 90px; color: #94a3b8; font-size: 11px; margin: auto;">
            M.Y.<br>(Möhür yeri)
        </div>
        <div style="width: 30%; text-align: right;">
            <div style="margin-bottom: 40px;"><strong>Təhvil verdi:</strong> ________________</div>
            <div><strong>Təhvil aldı:</strong> _________________</div>
        </div>
    </div>
</div>
"""
    frappe.get_doc({
        "doctype": "Print Format",
        "name": pf_name,
        "doc_type": "Sales Invoice",
        "standard": "No",
        "custom_format": 1,
        "print_format_type": "Jinja",
        "html": html_template
    }).insert(ignore_permissions=True)

    make_property_setter("Sales Invoice", "default_print_format", "default", pf_name, "Data", for_doctype=True)
    frappe.db.commit()
    print("   Azerbaijani Hesab-Faktura set as default print format.")

    # 13. Translations
    print("\n>>> 13. Applying Azerbaijani translations...")
    translations = [
        ("Müşteri", "Müştəri"),
        ("Tedarikçi", "Təchizatçı"),
        ("Satış Faturası", "Satış Qaiməsi"),
        ("Satınalma Faturası", "Alış Qaiməsi"),
        ("Sipariş", "Sifariş"),
        ("İrsaliye", "Qaimə"),
        ("Depo", "Anbar"),
        ("Stok", "Anbar"),
        ("Hesap Planı", "Hesablar Planı"),
        ("Bilanço", "Balans Hesabatı"),
        ("Gelir Tablosu", "Mənfəət və Zərər Hesabatı"),
        ("Muhasebe", "Mühasibatlıq"),
        ("Vergi Numarası", "VÖEN"),
        ("Tax ID", "VÖEN"),
        ("Kişisel", "Şəxsi"),
        ("Kullanıcılar", "İstifadəçilər"),
        ("Araçlar", "Alətlər"),
        ("İzinler", "Məzuniyyətlər"),
        ("Harcama Talepleri", "Xərc Tələbləri"),
        ("Bordro", "Əməkhaqqı Hesablanması"),
        ("İnsan Kaynakları", "İnsan Resursları (HR)")
    ]
    for src, trn in translations:
        if not frappe.db.exists("Translation", {"language": "tr", "source_text": src}):
            frappe.get_doc({
                "doctype": "Translation",
                "language": "tr",
                "source_text": src,
                "translated_text": trn
            }).insert(ignore_permissions=True)
        else:
            t = frappe.get_doc("Translation", {"language": "tr", "source_text": src})
            t.translated_text = trn
            t.save()
    frappe.db.commit()
    frappe.clear_cache()
    print("   Translations applied and cache cleared.")

    print("\n=======================================================")
    print("🎉 AZERBAIJAN LOCALIZATION & CHART OF ACCOUNTS COMPLETED 100%!")
    print("=======================================================")

if __name__ == "__main__":
    run()
