
import pandas as pd
from lxml import etree

# Load the Excel file with the final challan entries
df_final_updated = pd.read_excel("path_to_your_excel_file.xlsx")  # Replace with your actual file path

# Normalize and compare names
def normalize_name(name):
    return ''.join(e for e in name.lower().strip() if e.isalnum())

def has_special_characters(name):
    return any(char in name for char in ['&', '%', '#', '@', '!', '$', '*', '(', ')'])

def find_closest_match(name, ledger_list):
    normalized_name = normalize_name(name)
    for ledger_name in ledger_list:
        if normalize_name(ledger_name) == normalized_name:
            return ledger_name
    return None

# Mapping and generating XML for purchase entries
ledger_list_from_pdf = [
    "ABM & Brothers LH Payable", "ABM & Brothers LH Acc",
    "ABN Logistic India LH Payable", "ABN Logistic India LH Acc",
    "Adarsh Transport Co. LH Payable", "Adarsh Transport Co. LH Acc",
    # Add other ledger names here...
]

transporter_names_from_excel = df_final_updated['Transporter Name'].unique()
name_mapping_corrected = {}
unmatched_names_corrected = []

for name in transporter_names_from_excel:
    payable_match = find_closest_match(f"{name} LH Payable", ledger_list_from_pdf)
    acc_match = find_closest_match(f"{name} LH Acc", ledger_list_from_pdf)
    
    if payable_match and acc_match:
        name_mapping_corrected[name] = {
            "LH Payable": payable_match,
            "LH Acc": acc_match
        }
    else:
        unmatched_names_corrected.append(name)

# Ensure 'Challan No' is treated as a string
df_final_updated['Challan No'] = df_final_updated['Challan No'].astype(str)

# Generate XML
root_all_entries_final_corrected_retry = etree.Element("ENVELOPE")
header_all_entries_final_corrected_retry = etree.SubElement(root_all_entries_final_corrected_retry, "HEADER")
tallyrequest_all_entries_final_corrected_retry = etree.SubElement(header_all_entries_final_corrected_retry, "TALLYREQUEST")
tallyrequest_all_entries_final_corrected_retry.text = "Import Data"
body_all_entries_final_corrected_retry = etree.SubElement(root_all_entries_final_corrected_retry, "BODY")
importdata_all_entries_final_corrected_retry = etree.SubElement(body_all_entries_final_corrected_retry, "IMPORTDATA")
requestdesc_all_entries_final_corrected_retry = etree.SubElement(importdata_all_entries_final_corrected_retry, "REQUESTDESC")
reportname_all_entries_final_corrected_retry = etree.SubElement(requestdesc_all_entries_final_corrected_retry, "REPORTNAME")
reportname_all_entries_final_corrected_retry.text = "Vouchers"
staticvariables_all_entries_final_corrected_retry = etree.SubElement(requestdesc_all_entries_final_corrected_retry, "STATICVARIABLES")
svcompany_all_entries_final_corrected_retry = etree.SubElement(staticvariables_all_entries_final_corrected_retry, "SVCURRENTCOMPANY")
svcompany_all_entries_final_corrected_retry.text = "Nimbus Logistics FY 23-24"
requestdata_all_entries_final_corrected_retry = etree.SubElement(importdata_all_entries_final_corrected_retry, "REQUESTDATA")

for _, row in df_final_updated.iterrows():
    mapped_names = name_mapping_corrected.get(row['Transporter Name'], {})
    if mapped_names:
        tallymessage_all_entries_final_corrected_retry = etree.SubElement(requestdata_all_entries_final_corrected_retry, "TALLYMESSAGE", xmlns="TallyUDF")
        voucher_all_entries_final_corrected_retry = etree.SubElement(tallymessage_all_entries_final_corrected_retry, "VOUCHER", VCHTYPE="Purchase")
        date_all_entries_final_corrected_retry = etree.SubElement(voucher_all_entries_final_corrected_retry, "DATE")
        date_all_entries_final_corrected_retry.text = row['Challan Date'].strftime('%Y%m%d')
        guid_all_entries_final_corrected_retry = etree.SubElement(voucher_all_entries_final_corrected_retry, "GUID")
        guid_all_entries_final_corrected_retry.text = "Your_GUID_Here"
        vouchernumber_all_entries_final_corrected_retry = etree.SubElement(voucher_all_entries_final_corrected_retry, "VOUCHERNUMBER")
        vouchernumber_all_entries_final_corrected_retry.text = row['Challan No']
        if pd.isna(row['LR No']) or row['LR No'] == "-":
            narration_text_all_entries_final_corrected_retry = f"From {row['From']} to {row['To']} by vehicle {row['Vehicle Number']}"
        else:
            narration_text_all_entries_final_corrected_retry = f"From {row['From']} to {row['To']} by vehicle {row['Vehicle Number']}, LR No: {row['LR No']}"
        narration_all_entries_final_corrected_retry = etree.SubElement(voucher_all_entries_final_corrected_retry, "NARRATION")
        narration_all_entries_final_corrected_retry.text = narration_text_all_entries_final_corrected_retry
        partyledgername_all_entries_final_corrected_retry = etree.SubElement(voucher_all_entries_final_corrected_retry, "PARTYLEDGERNAME")
        partyledgername_all_entries_final_corrected_retry.text = mapped_names["LH Payable"]
        vouchertype_all_entries_final_corrected_retry = etree.SubElement(voucher_all_entries_final_corrected_retry, "VOUCHERTYPENAME")
        vouchertype_all_entries_final_corrected_retry.text = "Purchase"
        allledgerentries_all_entries_final_corrected_retry = etree.SubElement(voucher_all_entries_final_corrected_retry, "ALLLEDGERENTRIES.LIST")
        ledgername_all_entries_final_corrected_retry = etree.SubElement(allledgerentries_all_entries_final_corrected_retry, "LEDGERNAME")
        ledgername_all_entries_final_corrected_retry.text = mapped_names["LH Payable"]
        isdeemedpositive_all_entries_final_corrected_retry = etree.SubElement(allledgerentries_all_entries_final_corrected_retry, "ISDEEMEDPOSITIVE")
        isdeemedpositive_all_entries_final_corrected_retry.text = "No"
        amount_all_entries_final_corrected_retry = etree.SubElement(allledgerentries_all_entries_final_corrected_retry, "AMOUNT")
        amount_all_entries_final_corrected_retry.text = str(row['Total Challan Amount (Not Incl TDS Non Deductible Charges)'])
        allledgerentries_acc_all_entries_final_corrected_retry = etree.SubElement(voucher_all_entries_final_corrected_retry, "ALLLEDGERENTRIES.LIST")
        ledgername_acc_all_entries_final_corrected_retry = etree.SubElement(allledgerentries_acc_all_entries_final_corrected_retry, "LEDGERNAME")
        ledgername_acc_all_entries_final_corrected_retry.text = mapped_names["LH Acc"]
        isdeemedpositive_acc_all_entries_final_corrected_retry = etree.SubElement(allledgerentries_acc_all_entries_final_corrected_retry, "ISDEEMEDPOSITIVE")
        isdeemedpositive_acc_all_entries_final_corrected_retry.text = "Yes"
        amount_acc_all_entries_final_corrected_retry = etree.SubElement(allledgerentries_acc_all_entries_final_corrected_retry, "AMOUNT")
        amount_acc_all_entries_final_corrected_retry.text = str(-row['Total Challan Amount (Not Incl TDS Non Deductible Charges)'])

# Convert the etree to a string
xml_data_all_entries_final_corrected_output_retry = etree.tostring(root_all_entries_final_corrected_retry, pretty_print=True, xml_declaration=True, encoding="UTF-8")

# Save the XML to a file
with open("output_final_purchase_entries.xml", "wb") as file:
    file.write(xml_data_all_entries_final_corrected_output_retry)
