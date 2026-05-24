import requests
import time
import os
import threading
from datetime import datetime
from flask import Flask

# --- Настройки ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "-1003900711058"

app = Flask(__name__)

# --- Функции бота (те же, что и раньше) ---
def fetch_news():
    try:
        url = "https://cryptocurrency.cv/api/news"
        r = requests.get(url)
        data = r.json()
        items = data.get('news', [])[:5]
        result = []
        for item in items:
            result.append({
                'title': item.get('title', ''),
                'source': item.get('source', {}).get('name', 'Crypto'),
                'summary': item.get('description', '')[:300],
                'url': item.get('url', '')
            })
        return result
    except Exception as e:
        print(f"Ошибка при получении новостей: {e}")
        return []

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        })
    except Exception as e:
        print(f"Ошибка отправки: {e}")

def main():
    print(f"[{datetime.now()}] 🔄 Сбор новостей...")
    news = fetch_news()
    if not news:
        print("Новостей нет.")
        return
    for item in news:
        post = f"📰 *{item['title']}*\n\n{item['summary']}\n\n🔗 [Читать]({item['url']})"
        send_message(CHANNEL_ID, post)
        time.sleep(3)
    print(f"[{datetime.now()}] ✅ Готово!")

def schedule_checker():
    import schedule
    # Устанавливаем расписание
    schedule.every().day.at("10:00").do(main)
    schedule.every().day.at("15:00").do(main)
    schedule.every().day.at("19:00").do(main)
    
    print("⏰ Планировщик запущен. Ожидание времени...")
    while True:
        schedule.run_pending()
        time.sleep(60)

# --- Веб-сервер для Render ---
@app.route('/')
def home():
    return "News bot is running!", 200

@app.route('/health')
def health():
    return "OK", 200

# --- Запуск ---
if __name__ == "__main__":
    # Запускаем планировщик в отдельном потоке
    thread = threading.Thread(target=schedule_checker)
    thread.daemon = True
    thread.start()
    
    # Запускаем Flask-сервер (для порта)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
