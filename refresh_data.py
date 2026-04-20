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
# Using the ID from your browser: 1hqg0c7PGiEaxC-PpOuyCSfivwyhPKgS0mpbNIa55Zio
sheet = client.open_by_key('1hqg0c7PGiEaxC-PpOuyCSfivwyhPKgS0mpbNIa55Zio')
dash_tab = sheet.worksheet("dashboard")

# 3. Fetch Metrics (Adjust cell coordinates if you change the sheet layout)
data = {
    "metrics": {
        "net_pnl": dash_tab.acell('B6').value,
        "win_rate": dash_tab.acell('D6').value,
        "profit_factor": dash_tab.acell('F6').value,
        "total_trades": dash_tab.acell('B9').value,
        "expectancy": dash_tab.acell('B12').value,
        "open_risk": dash_tab.acell('H12').value  # Based on your Google Sheet structure
    }
}

# 4. Save to JSON
with open('data.json', 'w') as f:
    json.dump(data, f)
