from flask import Flask, request, abort
import os
import json
import hmac
import hashlib
import requests
from utils.sheet import add_registration

app = Flask(__name__)

# LINE 密鑰
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

def reply_message(reply_token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, data=json.dumps(body))

@app.route("/api/linewebhook", methods=["POST"])
def webhook():
    # 驗證簽名
    body = request.get_data(as_text=True)
    signature = request.headers["X-Line-Signature"]
    hash = hmac.new(LINE_CHANNEL_SECRET.encode('utf-8'), body.encode('utf-8'), hashlib.sha256).digest()
    computed_signature = hashlib.sha256(body.encode("utf-8")).digest()
    if signature != hmac.new(LINE_CHANNEL_SECRET.encode('utf-8'), body.encode('utf-8'), hashlib.sha256).digest().hex():
        abort(400)

    events = json.loads(body).get("events", [])
    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"]
            reply_token = event["replyToken"]
            user_id = event["source"]["userId"]

            # 簡化報名流程：若輸入「我要報名」，就自動幫他寫入一筆資料（用假資料）
            if text == "我要報名":
                # 假資料，之後你可以接收真實使用者選項
                mock_data = {
                    "user_id": user_id,
                    "name": "測試釣客",
                    "category": "釣手",
                    "items": {
                        "rod": 1,
                        "reel": 1,
                        "rig": 2,
                        "bait": 3,
                        "hook": 2,
                        "iron": 1,
                        "lead": 5
                    }
                }
                total = add_registration(mock_data)
                reply_message(reply_token, f"✅ 報名成功！總金額為 {total} 元")
            else:
                reply_message(reply_token, "請輸入「我要報名」來開始報名流程")

    return "OK"
