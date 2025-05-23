import gspread
import os
import json
from datetime import datetime

# 載入 Google Sheets API 金鑰（JSON 字串）
service_account_info = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
gc = gspread.service_account_from_dict(service_account_info)

# 連線到報名資料的 Google 試算表
sheet = gc.open_by_key(os.getenv("GOOGLE_SHEET_ID"))

# 預設使用的工作表名稱（例如：2025/5/30大物班報名資料表）
TAB_NAME = os.getenv("GOOGLE_SHEET_TAB_NAME")
worksheet = sheet.worksheet(TAB_NAME)

# 預設價格（可從 config 載入）
PRICES = {
    "rod": 300,
    "reel": 200,
    "rig": 50,
    "bait": 20,
    "hook": 10,
    "iron": 30,
    "lead": 15,
    "boat_fee": 950  # 可根據活動調整
}

def add_registration(data):
    """
    將報名資料寫入指定分頁
    data 是 dict 格式，包含：
        {
          "user_id": str,
          "name": str,
          "category": str,  # 釣手 or 觀光
          "items": dict     # 各裝備數量
        }
    """

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    items = data["items"]
    category = data["category"]

    # 計算金額
    rent_total = PRICES["rod"] * items["rod"] + PRICES["reel"] * items["reel"]
    buy_total = (
        PRICES["rig"] * items["rig"] +
        PRICES["bait"] * items["bait"] +
        PRICES["hook"] * items["hook"] +
        PRICES["iron"] * items["iron"] +
        PRICES["lead"] * items["lead"]
    )
    total = rent_total + buy_total + PRICES["boat_fee"]

    # 準備要寫入的資料列（照你的表格順序）
    row = [
        now,
        data["user_id"],
        data["name"],
        category,
        items["rod"],
        items["reel"],
        items["rig"],
        items["bait"],
        items["hook"],
        items["iron"],
        items["lead"],
        "Confirmed",
        total
    ]

    worksheet.append_row(row, value_input_option="USER_ENTERED")
    return total
