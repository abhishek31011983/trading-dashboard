import os
import json
import gspread
from google.oauth2.service_account import Credentials

# 1. Setup Google Access
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
secret_json = os.environ['GOOGLE_SHEET_KEY']
creds_dict = json.loads(secret_json)
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
client = gspread.authorize(creds)

# 2. Open your Sheet
sheet = client.open_by_key('1hqg0c7PGiEaxC-PpOuyCSfivwyhPKgS0mpbNIa55Zio')
dash_tab = sheet.worksheet("dashboard")
cash_tab = sheet.worksheet("All Trades")

# 3. Fetch Data
# Main Metrics
metrics = {
    "net_pnl": dash_tab.acell('B6').value,
    "win_rate": dash_tab.acell('D6').value,
    "profit_factor": dash_tab.acell('F6').value,
    "total_trades": dash_tab.acell('B9').value,
    "expectancy": dash_tab.acell('B12').value,
    "open_risk": dash_tab.acell('H12').value
}

# Monthly Data (Rows 15-26, Columns B & C)
monthly_labels = dash_tab.col_values(2)[14:26] # Column B (Month)
monthly_values = dash_tab.col_values(3)[14:26] # Column C (Closed P&L)

# Segment Data (Rows 15-21, Columns G & H)
segment_labels = dash_tab.col_values(7)[14:21] # Column G (Segment)
segment_values = dash_tab.col_values(8)[14:21] # Column H (P&L)

# Cash sheet data - all rows starting from row 2 (skip header)
cash_data_raw = cash_tab.get_all_values()
headers = cash_data_raw[0] if cash_data_raw else []
trades = []

for row in cash_data_raw[1:]:  # Skip header row
    if len(row) >= 11:  # Ensure row has enough columns
        trades.append({
            "status": row[0] if len(row) > 0 else "",
            "entry_date": row[1] if len(row) > 1 else "",
            "name": row[2] if len(row) > 2 else "",
            "current_price": row[3] if len(row) > 3 else "",
            "type": row[4] if len(row) > 4 else "",
            "instrument": row[5] if len(row) > 5 else "",
            "segment": row[6] if len(row) > 6 else "",
            "shares": row[7] if len(row) > 7 else "",
            "entry_price": row[8] if len(row) > 8 else "",
            "total_amount": row[9] if len(row) > 9 else "",
            "stop_loss": row[10] if len(row) > 10 else "",
            "risk_share": row[11] if len(row) > 11 else "",
            "total_risk": row[12] if len(row) > 12 else "",
            "tsl": row[13] if len(row) > 13 else "",
            "open_risk_share": row[14] if len(row) > 14 else "",
            "total_open_risk": row[15] if len(row) > 15 else "",
            "portfolio_size": row[16] if len(row) > 16 else "",
            "risk_on_portfolio": row[17] if len(row) > 17 else "",
            "exit_price": row[18] if len(row) > 18 else "",
            "pl_share": row[19] if len(row) > 19 else "",
            "total_pl": row[20] if len(row) > 20 else "",
            "rr_achieved": row[21] if len(row) > 21 else "",
            "comments": row[22] if len(row) > 22 else "",
            "market_conditions": row[23] if len(row) > 23 else ""
        })

# Fetch Open Risk data
open_risk_cash_tab = sheet.worksheet("Open Risk - Cash")
open_risk_derivatives_tab = sheet.worksheet("Open Risk - Derivatives")

# Get Cash Open Risk data (skip header)
cash_risk_raw = open_risk_cash_tab.get_all_values()
cash_risk_data = []
if len(cash_risk_raw) > 1:
    for row in cash_risk_raw[1:]:
        if len(row) >= 2 and row[0]:  # Has stock name
            cash_risk_data.append({
                "stock": row[0],
                "open_risk": row[1] if len(row) > 1 else ""
            })

# Get Derivatives Open Risk data (skip header)
derivatives_risk_raw = open_risk_derivatives_tab.get_all_values()
derivatives_risk_data = []
if len(derivatives_risk_raw) > 1:
    for row in derivatives_risk_raw[1:]:
        if len(row) >= 2 and row[0]:  # Has symbol name
            derivatives_risk_data.append({
                "symbol": row[0],
                "open_risk": row[1] if len(row) > 1 else ""
            })


data = {
    "metrics": metrics,
    "charts": {
        "monthly": {"labels": monthly_labels, "values": monthly_values},
        "segment": {"labels": segment_labels, "values": segment_values}
    },
    "trades": trades,
        "open_risk": {
        "cash": cash_risk_data,
        "derivatives": derivatives_risk_data
    },
    "headers": headers
}

# 4. Save to JSON
with open('data.json', 'w') as f:
    json.dump(data, f)
