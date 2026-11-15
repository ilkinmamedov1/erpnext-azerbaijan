import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def run():
    frappe.init(site="frontend", sites_path="/home/frappe/frappe-bench/sites")
    frappe.connect()
    company_name = "TEST MMC"
    abbr = "TM"

    print(">>> 1. Configuring Company Details (TEST MMC)...")
    comp = frappe.get_doc("Company", company_name)
    comp.tax_id = "1300000001"
    comp.default_currency = "AZN"
    comp.accumulated_depreciation_account = f"112.06 - Digər TTA üzrə amortizasiya - {abbr}"
    comp.depreciation_expense_account = f"721.08 - TTA amortizasiyası (inzibati) - {abbr}"
    comp.capital_work_in_progress_account = f"113 - TTA ilə bağlı məsrəflərin kapitallaşdırılması - {abbr}"
    comp.disposal_account = f"731.04 - Aktivlərin silinməsi zərərləri - {abbr}"
    comp.asset_received_but_not_billed = f"531.05 - Fakturası daxil olmamış mallar üzrə borclar - {abbr}"
    comp.expenses_included_in_asset_valuation = None
    comp.expenses_included_in_valuation = None
    comp.save()
    frappe.db.commit()
    print("   Company tax_id updated to 1300000001 (VÖEN) and asset accounts linked.")

    print(">>> 2. Configuring Bank and Bank Account...")
    if not frappe.db.exists("Bank", "Kapital Bank ASC"):
        bank = frappe.get_doc({
            "doctype": "Bank",
            "bank_name": "Kapital Bank ASC",
            "swift_number": "AIIBAZ2X"
        }).insert(ignore_permissions=True)
    
    bank_account_name = f"{company_name} - Kapital Bank Əsas Hesab"
    if not frappe.db.exists("Bank Account", bank_account_name):
        frappe.get_doc({
            "doctype": "Bank Account",
            "account_name": bank_account_name,
            "bank": "Kapital Bank ASC",
            "account": f"223.01 - Bank hesabı - AZN (Əsas bank) - {abbr}",
            "company": company_name,
            "is_company_account": 1,
            "is_default": 1,
            "iban": "AZ43AIIB38010019440026214101",
            "branch_code": "200178"
        }).insert(ignore_permissions=True)
    frappe.db.commit()
    print("   Bank and Bank Account created and linked to 223.01.")

    print(">>> 3. Configuring Tax Templates (ƏDV 18%, 0%, Əvəzləşdirilən)...")
    # Clean up old broken templates if any
    if frappe.db.exists("Sales Taxes and Charges Template", f"Azerbaijan Tax - {abbr}"):
        frappe.delete_doc("Sales Taxes and Charges Template", f"Azerbaijan Tax - {abbr}", force=True)
    
    # Sales Taxes: ƏDV 18%
    sales_tax_18 = f"ƏDV 18% - {abbr}"
    if frappe.db.exists("Sales Taxes and Charges Template", sales_tax_18):
        frappe.delete_doc("Sales Taxes and Charges Template", sales_tax_18, force=True)
    
    st_doc = frappe.get_doc({
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

    # Sales Taxes: ƏDV 0% (İxrac)
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

    # Sales Taxes: ƏDV-dən Azad
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

    # Purchase Taxes: ƏDV 18% (Yerli alışlar)
    purch_tax_18 = f"ƏDV 18% (Yerli alışlar) - {abbr}"
    if frappe.db.exists("Purchase Taxes and Charges Template", purch_tax_18):
        frappe.delete_doc("Purchase Taxes and Charges Template", purch_tax_18, force=True)
    
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

    # Purchase Taxes: ƏDV 18% (İdxal)
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
    print("   Sales & Purchase Tax templates created successfully!")

    print(">>> 4. Configuring Modes of Payment...")
    payment_modes = [
        ("Nağd (Kassa)", "Cash", f"221.01 - Kassa - AZN - {abbr}"),
        ("Bank köçürməsi (AZN)", "Bank", f"223.01 - Bank hesabı - AZN (Əsas bank) - {abbr}"),
        ("POS-Terminal / Kart", "Bank", f"223.01 - Bank hesabı - AZN (Əsas bank) - {abbr}"),
        ("ƏDV Depozit Hesabı", "Bank", f"226 - ƏDV sub-uçot hesabı - {abbr}")
    ]
    for mode_name, mode_type, account_name in payment_modes:
        if not frappe.db.exists("Mode of Payment", mode_name):
            doc = frappe.get_doc({
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
    
    for old_mode in ["Kontrol etmek", "Kredi Kartı", "Elektronik Transfer", "Banka Havalesi"]:
        if frappe.db.exists("Mode of Payment", old_mode):
            m = frappe.get_doc("Mode of Payment", old_mode)
            m.enabled = 0
            m.save()
    frappe.db.commit()
    print("   Modes of Payment configured cleanly!")

    print(">>> 5. Configuring Warehouses...")
    wh_renames = [
        (f"Tüm Depolar - {abbr}", f"Bütün Anbarlar - {abbr}", 1, None),
        (f"Mağazalar - {abbr}", f"Əsas Anbar (Mallar) - {abbr}", 0, f"205.01 - Mallar - anbar - {abbr}"),
        (f"Mamüller - {abbr}", f"Hazır Məhsul Anbarı - {abbr}", 0, f"204 - Hazır məhsul - {abbr}"),
        (f"Devam ediyor - {abbr}", f"Bitməmiş İstehsalat Anbarı - {abbr}", 0, f"202 - İstehsalat məsrəfləri (bitməmiş ist.) - {abbr}"),
        (f"Transit Ürünler - {abbr}", f"Tranzit Anbar (Yolda olan mallar) - {abbr}", 0, f"207 - Digər ehtiyatlar - {abbr}")
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
            "account": f"201 - Material ehtiyatları - {abbr}"
        }).insert(ignore_permissions=True)
    
    stock_settings = frappe.get_doc("Stock Settings")
    stock_settings.default_warehouse = f"Əsas Anbar (Mallar) - {abbr}"
    stock_settings.save()
    frappe.db.commit()
    print("   Warehouses restructured and Azerbaijani names applied!")

    print(">>> 6. Configuring Units of Measure (UOM)...")
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
    print("   UOMs created successfully!")

    print(">>> 7. Configuring Property Setters (VÖEN & Naming Series)...")
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
    print("   VÖEN labels and Naming Series configured!")

    print(">>> 8. Configuring Currency Exchange Rates (CBAR Reference)...")
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
    print("   Today's CBAR benchmark exchange rates inserted!")

    print(">>> 9. Creating Custom Azerbaijani Print Format (Hesab-Faktura)...")
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
                <div><strong>Bank:</strong> Kapital Bank ASC</div>
                <div><strong>Kod / MFO:</strong> 200178 | <strong>SWIFT:</strong> AIIBAZ2X</div>
                <div><strong>İBAN:</strong> AZ43AIIB38010019440026214101</div>
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
    print("   Azerbaijani Hesab-Faktura print format created and set as default!")

    print(">>> 10. Adding Key Translations...")
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
    print("   Custom translations applied successfully!")

    print("\nALL AZERBAIJAN LOCALIZATIONS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run()
