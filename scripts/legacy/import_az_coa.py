import csv
import frappe
from frappe.utils.nestedset import rebuild_tree

def run():
    frappe.init(site="frontend")
    frappe.connect()

    company = "TEST MMC"
    abbr = frappe.db.get_value("Company", company, "abbr") or "TM"
    print(f"Company: {company}, Abbreviation: {abbr}")

    # Check GL Entries
    gl_count = frappe.db.count("GL Entry", {"company": company})
    if gl_count > 0:
        print(f"ERROR: {gl_count} GL Entries exist for {company}. Cannot wipe accounts.")
        return

    # Clear Mode of Payment Account link
    frappe.db.sql("DELETE FROM `tabMode of Payment Account` WHERE company = %s", (company,))

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
            discount_allowed_account = NULL,
            discount_received_account = NULL,
            exchange_gain_loss_account = NULL,
            unrealized_exchange_gain_loss_account = NULL
        WHERE name = %s
    """, (company,))

    # Delete existing accounts of TEST MMC
    old_accounts = frappe.db.get_all("Account", filters={"company": company}, pluck="name")
    print(f"Removing {len(old_accounts)} temporary accounts created by setup wizard...")
    frappe.db.sql("DELETE FROM `tabAccount` WHERE company = %s", (company,))

    # Read CSV
    csv_path = "/home/frappe/frappe-bench/sites/azerbaijan_coa.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Total rows in CSV: {len(rows)}")

    # Index by account number
    num_to_row = {}
    for r in rows:
        num = r["Account Number"].strip()
        num_to_row[num] = r

    # Build full names (IDs)
    # format: {num} - {name} - {abbr}
    id_map = {}
    for num, r in num_to_row.items():
        name = r["Account Name"].strip()
        full_id = f"{num} - {name} - {abbr}"
        id_map[num] = full_id

    # Topological sort (parents must be inserted before children)
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

                # Specific Account Type adjustments for Tax accounts
                if num in ["241", "241.01", "241.02", "521", "521.01"]:
                    if not acct_type:
                        acct_type = "Tax"

                doc = frappe.new_doc("Account")
                doc.name = full_id
                doc.account_number = num
                doc.account_name = acct_name
                doc.company = company
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

    print(f"Successfully inserted {inserted_count} accounts!")

    # Add Stock Received But Not Billed helper under 531 if not exists
    srbnb_id = f"531.05 - Fakturası daxil olmamış mallar üzrə borclar - {abbr}"
    if not frappe.db.exists("Account", srbnb_id):
        srbnb = frappe.new_doc("Account")
        srbnb.name = srbnb_id
        srbnb.account_number = "531.05"
        srbnb.account_name = "Fakturası daxil olmamış mallar üzrə borclar"
        srbnb.company = company
        srbnb.parent_account = id_map.get("531", f"531 - Malsatanlara qısamüddətli kreditor borcları - {abbr}")
        srbnb.is_group = 0
        srbnb.root_type = "Liability"
        srbnb.report_type = "Balance Sheet"
        srbnb.account_currency = "AZN"
        srbnb.account_type = "Stock Received But Not Billed"
        srbnb.flags.ignore_validate = True
        srbnb.insert()
        print(f"Created: {srbnb_id}")

    # Rebuild nested set tree
    print("Rebuilding tree lft/rgt...")
    rebuild_tree("Account", "parent_account")

    # Link default company accounts
    def get_id(num, default=None):
        return id_map.get(num, default)

    cash_acct = get_id("221.01") # Kassa - AZN
    bank_acct = get_id("223.01") # Bank hesabı - AZN (Əsas bank)
    recv_acct = get_id("211.01.01") # Yerli alıcılar - hüquqi şəxslər
    pay_acct = get_id("531.01.01") # Yerli malsatanlar - hüquqi şəxslər
    stock_acct = get_id("205.01") # Mallar - anbar
    income_acct = get_id("601.02.01") # Mal satışı - pərakəndə
    expense_acct = get_id("701.04") # Alınan malların dəyəri (SDX)
    stock_adj = get_id("208") # Ehtiyatların dəyər düzəlişi
    round_off = get_id("721.19") # Digər inzibati xərclər
    ex_gain_loss = get_id("631.04") # Valyuta məzənnə fərqi (mənfəət)

    frappe.db.set_value("Company", company, {
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
    print("Updated Company default accounts successfully!")

    # Set Mode of Payment Nakit default account
    mop = frappe.db.get_value("Mode of Payment", {"name": "Nakit"}, "name")
    if mop:
        mop_doc = frappe.get_doc("Mode of Payment", mop)
        mop_doc.set("accounts", [])
        mop_doc.append("accounts", {
            "company": company,
            "default_account": cash_acct
        })
        mop_doc.save()
        print("Updated Mode of Payment 'Nakit' default account to Kassa - AZN")

    frappe.db.commit()
    frappe.clear_cache()
    print("ALL DONE! 100% SUCCESS!")

run()
