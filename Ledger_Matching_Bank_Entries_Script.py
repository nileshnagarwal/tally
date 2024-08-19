'''
First prepare the Tally Export File: https://docs.google.com/spreadsheets/d/12H_Qk2WhTJ8GK7muxwaaKKN6OMOEtA3V8peVecRyUwY/edit?gid=216096852#gid=216096852
Then run the below script which will create ledger mapping for majority of the rows. 
Finally run the bank.py script from https://github.com/nileshnagarwal/tally using chatgpt to convert Excel to XML
The script is designed to work with Json but chatgpt can convert it to work with excel and generate the XML for downloading.
'''

# Refined function to match narration with ledger names based on the rules provided
def match_ledger_refined(narration, ledgers):
    # Check for exact matches first
    for ledger in ledgers:
        if ledger.lower() in narration.lower():
            return ledger
    
    # Check for personal expenses and specific names
    if any(keyword in narration.lower() for keyword in ["barber", "doctor", "personal"]):
        return "Nilesh Agarwal"
    
    # Last attempt to match based on common name segments
    for ledger in ledgers:
        if any(word in ledger.lower() for word in narration.lower().split('/')):
            return ledger
    
    # If no match is found, return a placeholder for manual checking
    return "Manual Check Required"

# Reapply the matching logic with the refined function
matched_ledgers_refined = []
for narration in narrations:
    matched_ledger = match_ledger_refined(narration, df_ledgers_final)
    matched_ledgers_refined.append(matched_ledger)

# Update the bank statement with the refined matched ledgers
df_bank_statement['Matched Ledger'] = matched_ledgers_refined

# Save the updated bank statement to an Excel file for inspection
output_excel_path_refined = "/mnt/data/Refined_Bank_Statement_with_Ledgers.xlsx"
df_bank_statement.to_excel(output_excel_path_refined, index=False)

output_excel_path_refined
