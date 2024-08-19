import pandas as pd
import xml.etree.ElementTree as ET
from difflib import get_close_matches

# Function to validate critical columns in the data
def validate_data_before_xml(df, critical_columns):
    nan_issues = df[critical_columns].isna().sum()
    issues = nan_issues[nan_issues > 0]
    
    if not issues.empty:
        raise ValueError(f"Critical NaN values found in the following columns:\n{issues}")
    
    zero_issues_freight = df[df['Freight Amount'] == 0]
    
    if not zero_issues_freight.empty:
        invoice_numbers_with_zero_freight = zero_issues_freight['Invoice No'].tolist()
        raise ValueError(f"Zero values found in the Freight Amount column for Invoice Numbers: {invoice_numbers_with_zero_freight}")
    
    return "Data validation passed."

# Function to match client names to ledger names
def match_ledger_names(client_names, ledger_names):
    matched = {}
    unmatched = []

    for client_name in client_names:
        match = get_close_matches(client_name, ledger_names, n=1, cutoff=0.7)
        if match:
            matched[client_name] = match[0]
        else:
            unmatched.append(client_name)
    
    return matched, unmatched

# Function to create ledger entries XML if needed
def create_ledger_entries_xml(ledger_names, output_xml_path):
    root = ET.Element("ENVELOPE")
    
    header = ET.SubElement(root, "HEADER")
    tallyRequest = ET.SubElement(header, "TALLYREQUEST").text = "Import Data"

    body = ET.SubElement(root, "BODY")
    importData = ET.SubElement(body, "IMPORTDATA")

    requestDesc = ET.SubElement(importData, "REQUESTDESC")
    reportName = ET.SubElement(requestDesc, "REPORTNAME").text = "All Masters"

    staticVariables = ET.SubElement(requestDesc, "STATICVARIABLES")
    svCurrentCompany = ET.SubElement(staticVariables, "SVCURRENTCOMPANY").text = "Your Company Name"

    requestData = ET.SubElement(importData, "REQUESTDATA")

    for ledger_name in ledger_names:
        tallyMessage = ET.SubElement(requestData, "TALLYMESSAGE", xmlns="TallyUDF")
        ledger = ET.SubElement(tallyMessage, "LEDGER", NAME=ledger_name)

        guid = ET.SubElement(ledger, "GUID")
        guid.text = "GUID-" + ledger_name.replace(" ", "")  # Example GUID creation
        parent = ET.SubElement(ledger, "PARENT")
        parent.text = "Clients"
        isDeemedPositive = ET.SubElement(ledger, "ISDEEMEDPOSITIVE")
        isDeemedPositive.text = "Yes"
        alterID = ET.SubElement(ledger, "ALTERID")
        alterID.text = "ALTERID-" + ledger_name.replace(" ", "")
        openingBalance = ET.SubElement(ledger, "OPENINGBALANCE")
        openingBalance.text = "0"

        languageNameList = ET.SubElement(ledger, "LANGUAGENAME.LIST")
        nameList = ET.SubElement(languageNameList, "NAME.LIST", TYPE="String")
        name = ET.SubElement(nameList, "NAME")
        name.text = ledger_name
        languageID = ET.SubElement(languageNameList, "LANGUAGEID")
        languageID.text = "1033"

    xml_string = ET.tostring(root, encoding='unicode', method='xml')
    
    with open(output_xml_path, "w", encoding='utf-8') as file:
        file.write(xml_string)
    
    return f"Ledger creation XML generated successfully at {output_xml_path}"

# Function to create bill entries XML
def create_bill_xml_string(df):
    root = ET.Element("ENVELOPE")
    
    header = ET.SubElement(root, "HEADER")
    tallyRequest = ET.SubElement(header, "TALLYREQUEST").text = "Import Data"

    body = ET.SubElement(root, "BODY")
    importData = ET.SubElement(body, "IMPORTDATA")

    requestDesc = ET.SubElement(importData, "REQUESTDESC")
    reportName = ET.SubElement(requestDesc, "REPORTNAME").text = "Vouchers"

    staticVariables = ET.SubElement(requestDesc, "STATICVARIABLES")
    svCurrentCompany = ET.SubElement(staticVariables, "SVCURRENTCOMPANY").text = "Your Company Name"

    requestData = ET.SubElement(importData, "REQUESTDATA")

    for _, obj in df.iterrows():
        tallyMessage = ET.SubElement(requestData, "TALLYMESSAGE", {"xmlns:UDF": "TallyUDF"})
        voucher = ET.SubElement(tallyMessage, "VOUCHER", {"ACTION": "Create", "VCHTYPE": "Sales"})
        voucherTypeName = ET.SubElement(voucher, "VOUCHERTYPENAME").text = "Sales"
        
        dt_object = obj["Invoice Date"]
        date = ET.SubElement(voucher, "DATE").text = dt_object.strftime("%Y%m%d")
        
        reference = ET.SubElement(voucher, "REFERENCE")
        narration = ET.SubElement(voucher, "NARRATION").text = f"{obj['From']}. {obj['Vehicle Number']}. FM{obj['Challan No']} Comments: {obj.get('Comments', '')}. Detention: {obj.get('Note for Detention Charges', '')}"
        
        partyName = ET.SubElement(voucher, "PARTYNAME").text = obj["Client Name"]
        voucherNumber = ET.SubElement(voucher, "VOUCHERNUMBER").text = str(obj["Modified Invoice No"])
        guid = ET.SubElement(voucher, "GUID")
        alterID = ET.SubElement(voucher, "ALTERID")
        
        clientAmount = "-" + str(round(float(obj["Freight Amount"]), 2))
        gst_amount = float(obj["GST (Payable by Us)"]) if not pd.isna(obj["GST (Payable by Us)"]) else 0
        if gst_amount:
            arr = [1, 2, 3]
            freightForwardingAmount = str(round(round(float(obj["Freight Amount"]), 2) - round(gst_amount, 2), 2))
            gstAmount = str(round(gst_amount, 2))
        else:
            arr = [1, 2]
            freightForwardingAmount = str(round(float(obj["Freight Amount"]), 2))
        
        for n in arr:
            allLedgerEntries = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
            removeZeroEntries = ET.SubElement(allLedgerEntries, "REMOVEZEROENTRIES").text = "No"
            isDeemedPositive = ET.SubElement(allLedgerEntries, "ISDEEMEDPOSITIVE")
            if n == 1:
                isDeemedPositive.text = "Yes"
                ledgerName = ET.SubElement(allLedgerEntries, "LEDGERNAME").text = obj["Client Name"]
                isPartyLedger = ET.SubElement(allLedgerEntries, "ISPARTLEDGER").text = "Yes"
                isLastDeemedPositive = ET.SubElement(allLedgerEntries, "ISLASTDEEMEDPOSITIVE").text = "Yes"
                amount = ET.SubElement(allLedgerEntries, "AMOUNT").text = clientAmount
                billAllocations = ET.SubElement(allLedgerEntries, "BILLALLOCATIONS.LIST")
                billAllocationsName = ET.SubElement(billAllocations, "NAME").text = str(obj["Modified Invoice No"])
                billAllocationsBillType = ET.SubElement(billAllocations, "BILLTYPE").text = "New Ref"
                billAllocationsAmount = ET.SubElement(billAllocations, "AMOUNT").text = clientAmount
            elif n == 2:
                isDeemedPositive.text = "No"
                ledgerName = ET.SubElement(allLedgerEntries, "LEDGERNAME").text = "Freight Forwarding (MH)"
                isPartyLedger = ET.SubElement(allLedgerEntries, "ISPARTLEDGER").text = "No"
                isLastDeemedPositive = ET.SubElement(allLedgerEntries, "ISLASTDEEMEDPOSITIVE").text = "No"
                amount = ET.SubElement(allLedgerEntries, "AMOUNT").text = freightForwardingAmount
            elif n == 3:
                isDeemedPositive.text = "No"
                ledgerName = ET.SubElement(allLedgerEntries, "LEDGERNAME").text = "GST Payable"
                isPartyLedger = ET.SubElement(allLedgerEntries, "ISPARTLEDGER").text = "No"
                isLastDeemedPositive = ET.SubElement(allLedgerEntries, "ISLASTDEEMEDPOSITIVE").text = "No"
                amount = ET.SubElement(allLedgerEntries, "AMOUNT").text = gstAmount
    
    xml_string = ET.tostring(root, encoding='unicode', method='xml')
    return xml_string

# Main function to process Excel file and generate XMLs
def process_excel_file(file_path, ledger_names, output_xml_path, ledger_creation_xml_path):
    # Load the Excel file
    df = pd.read_excel(file_path)

    # Validate the data
    critical_columns = ['Client Name', 'Freight Amount', 'GST (Payable by Us)', 'Invoice No', 'Invoice Date']
    validate_data_before_xml(df, critical_columns)

    # Match client names with ledger names
    client_names = df['Client Name'].unique()
    matched_ledgers, unmatched_clients = match_ledger_names(client_names, ledger_names)

    # Instructions for the LLM to handle unmatched clients:
    # 1. For each unmatched client, manually check for close matches in the list of ledger names.
    # 2. If the LLM finds a near match with minor spelling differences, it should confirm with the user before making a correction.
    # 3. If there are no matches, alert the user and ask if they would like to create new ledgers for these clients.

    # If the user instructs to create new ledgers, proceed with ledger creation
    if unmatched_clients:
        create_ledger_entries_xml(unmatched_clients, ledger_creation_xml_path)
        raise ValueError(f"Unmatched clients found: {unmatched_clients}. Ledger creation XML has been generated at {ledger_creation_xml_path}. Please review and re-run after the ledgers are created.")

    # Re-create the "Modified Invoice No" column
    df['Modified Invoice No'] = df['Invoice No'].apply(lambda x: f"24-25/{int(x):03d}")

    # Clean up the "Freight Amount" and "GST (Payable by Us)" columns
    df['Freight Amount'] = df['Freight Amount'].replace('[\₹,/-]', '', regex=True).astype(float)
    df['GST (Payable by Us)'] = df['GST (Payable by Us)'].replace('[\₹,/-]', '', regex=True).astype(float)

    # Generate the XML content for bill entries
    xml_content = create_bill_xml_string(df)

    # Save the XML content to a file
    with open(output_xml_path, "w", encoding='utf-8') as file:
        file.write(xml_content)
    
    return f"Bill entries XML generated successfully at {output_xml_path}"

# Example usage:
# ledger_names = ["Ador Welding Limited", "Chandra Equipments", "Omniscient Process Equipments Private Limited"] # Populate with actual ledger names
# result = process_excel_file("Sample Bill Entries in Excel.xlsx", ledger_names, "Tally_Bill_Import.xml", "Tally_Ledger_Creation.xml")
# print(result)

'''
Instructions for the LLM (ChatGPT or Similar):
Initial Setup:

Upload the Excel file and provide the list of existing ledger names in Tally.
Specify the paths where the output XML files should be saved.
Matching Ledger Names:

The LLM should compare each client name in the Excel sheet with the provided ledger names.
If there is no exact match, the LLM should look for close matches (e.g., similar spelling) and present these to the user for manual review.
If no suitable matches are found, the LLM should alert the user and ask whether to create new ledgers for these unmatched clients.
Manual Review:

The LLM should facilitate a manual check for any close matches, asking the user to confirm if a near match should be used or if a new ledger should be created.
This step ensures that only correctly matched or newly created ledgers are used in the final XML.
Data Validation:

Before generating the XML, the LLM should ensure that there are no NaN or zero values in critical columns ("Freight Amount," "Invoice No," etc.).
If any issues are detected, the LLM should halt the process and alert the user, providing the invoice numbers that need correction.
Ledger Creation (if needed):

If instructed, the LLM will generate an XML file for creating the necessary ledger entries in Tally and alert the user to import this file into Tally before proceeding with the bill entries.
Generating the Final XML:

After all validations and checks are complete, the LLM should generate the XML file for bill entries and save it to the specified path.
The LLM should then inform the user that the process is complete and provide the download link for the XML file.
'''