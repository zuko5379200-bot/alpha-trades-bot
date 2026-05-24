import os
import time
import threading
from flask import Flask

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "-1003900711058"

def send_test():
    import requests
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHANNEL_ID, "text": "✅ Бот жив и работает!"})
    except Exception as e:
        print(e)

@app.route('/')
def home():
    return "News bot is running!", 200

if __name__ == "__main__":
    # Отправляем тест через 10 секунд после запуска
    timer = threading.Timer(10.0, send_test)
    timer.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
