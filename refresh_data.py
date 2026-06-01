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
all_trades_tab = sheet.worksheet("All Trades")
account_size_tab = sheet.worksheet("Account Size")
charges_tab = sheet.worksheet("Charges")

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
monthly_labels = dash_tab.col_values(2)[14:26]
monthly_values = dash_tab.col_values(3)[14:26]

# Segment Data (Rows 15-21, Columns G & H)
segment_labels = dash_tab.col_values(7)[14:21]
segment_values = dash_tab.col_values(8)[14:21]

# All Trades sheet
all_trades_raw = all_trades_tab.get_all_values()
headers = all_trades_raw[0] if all_trades_raw else []
trades = []
for row in all_trades_raw[1:]:
    if len(row) >= 11:
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
            "risk_per_share": row[11] if len(row) > 11 else "",
            "total_risk": row[12] if len(row) > 12 else "",
            "tsl": row[13] if len(row) > 13 else "",
            "open_risk_per_share_unit": row[14] if len(row) > 14 else "",
            "total_open_risk": row[15] if len(row) > 15 else "",
            "portfolio_size": row[17] if len(row) > 17 else "",
            "risk_on_portfolio": row[18] if len(row) > 18 else "",
            "exit_date": row[19] if len(row) > 19 else "",
            "exit_price": row[20] if len(row) > 20 else "",
            "total_pl": row[21] if len(row) > 21 else "",
            "entry_charges": row[22] if len(row) > 22 else "",
            "exit_charges": row[23] if len(row) > 23 else "",
            "mtf_interest": row[24] if len(row) > 24 else "",
            "rr_achieved": row[25] if len(row) > 25 else "",
            "comments": row[26] if len(row) > 26 else "",
            "market_conditions": row[27] if len(row) > 27 else ""
        })

# Open Risk tabs
open_risk_cash_tab = sheet.worksheet("Open Risk - Cash")
open_risk_derivatives_tab = sheet.worksheet("Open Risk - Derivatives")

cash_risk_raw = open_risk_cash_tab.get_all_values()
cash_risk_data = []
if len(cash_risk_raw) > 1:
    for row in cash_risk_raw[1:]:
        if len(row) >= 2 and row[0]:
            cash_risk_data.append({"stock": row[0], "open_risk": row[1] if len(row) > 1 else ""})

derivatives_risk_raw = open_risk_derivatives_tab.get_all_values()
derivatives_risk_data = []
if len(derivatives_risk_raw) > 1:
    for row in derivatives_risk_raw[1:]:
        if len(row) >= 2 and row[0]:
            derivatives_risk_data.append({"symbol": row[0], "open_risk": row[1] if len(row) > 1 else ""})

# Account Size tab — columns A:D (Date, Nifty Close, Deposits/Withdrawals, Portfolio Size)
account_raw = account_size_tab.get_all_values()
account_data = []
if len(account_raw) > 1:
    for row in account_raw[1:]:
        if len(row) >= 4 and row[0]:
            account_data.append({
                "date": row[0],
                "nifty_close": row[1] if len(row) > 1 else "",
                "deposit_withdrawal": row[2] if len(row) > 2 else "",
                "portfolio_size": row[3] if len(row) > 3 else ""
            })

# Charges tab — weekly breakdown and FY totals
charges_raw = charges_tab.get_all_values()
weekly_charges = []
fy_charges = []

for i, row in enumerate(charges_raw):
    if not row:
        continue
    if row[0] == 'Week of':
        for data_row in charges_raw[i + 1:]:
            if not data_row or not data_row[0]:
                break
            weekly_charges.append({
                "week": data_row[0],
                "net_profit": data_row[1] if len(data_row) > 1 else "",
                "cash_profit": data_row[2] if len(data_row) > 2 else "",
                "cash_charges": data_row[3] if len(data_row) > 3 else "",
                "fo_profit": data_row[5] if len(data_row) > 5 else "",
                "fo_charges": data_row[6] if len(data_row) > 6 else "",
            })
        break

for i, row in enumerate(charges_raw):
    if not row:
        continue
    if row[0] == 'Financial Year':
        for data_row in charges_raw[i + 1:]:
            if not data_row or not data_row[0]:
                break
            fy_charges.append({
                "fy": data_row[0],
                "cash_charges": data_row[1] if len(data_row) > 1 else "",
                "fo_charges": data_row[2] if len(data_row) > 2 else "",
                "total": data_row[3] if len(data_row) > 3 else "",
            })
        break

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
    "account_growth": account_data,
    "charges": {
        "weekly": weekly_charges,
        "fy": fy_charges
    },
    "headers": headers
}

with open('data.json', 'w') as f:
    json.dump(data, f)
