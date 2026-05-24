import requests
import time
import os
import threading
from datetime import datetime
from flask import Flask

# --- Настройки ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "-1003900711058"

NEWS_API_URL = "https://cryptocurrency.cv/api/news?lang=ru"

app = Flask(__name__)

def fetch_news():
    try:
        print(f"[{datetime.now()}] Запрашиваю новости на русском...")
        r = requests.get(NEWS_API_URL, timeout=10)
        data = r.json()
        articles = data.get('articles', data.get('news', []))
        if not articles:
            print("Новости не найдены.")
            return []
        items = articles[:5]
        result = []
        for item in items:
            image_url = None
            if 'urlToImage' in item and item['urlToImage']:
                image_url = item['urlToImage']
            elif 'image' in item and item['image']:
                image_url = item['image']
            elif 'media' in item and item['media']:
                image_url = item['media']
            result.append({
                'title': item.get('title', 'Без заголовка'),
                'source': item.get('source', {}).get('name', 'Crypto News'),
                'summary': item.get('description', '')[:300],
                'url': item.get('url', ''),
                'image': image_url
            })
        print(f"Найдено {len(result)} новостей")
        return result
    except Exception as e:
        print(f"Ошибка: {e}")
        return []

def send_photo_with_caption(chat_id, image_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        response = requests.post(url, json={
            "chat_id": chat_id,
            "photo": image_url,
            "caption": caption,
            "parse_mode": "Markdown"
        })
        print(f"Фото, статус: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка фото: {e}")
        return False

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        })
        print(f"Текст, статус: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def format_caption(news_item):
    caption = (
        f"📰 *{news_item['title']}*\n\n"
        f"{news_item['summary']}\n\n"
        f"🔗 [Читать полностью]({news_item['url']})\n"
        f"---\n"
        f"💡 *Alpha Trades*"
    )
    return caption

def main():
    print(f"[{datetime.now()}] 🔄 Запуск...")
    news = fetch_news()
    if not news:
        print("Нет новостей.")
        return
    for i, item in enumerate(news):
        caption = format_caption(item)
        if item['image']:
            send_photo_with_caption(CHANNEL_ID, item['image'], caption)
        else:
            send_message(CHANNEL_ID, caption)
        time.sleep(3)
    print(f"[{datetime.now()}] ✅ Готово! {len(news)} постов")

def schedule_checker():
    import schedule
    # Время указано для Орегона (UTC-7)
    # 15:20 МСК = 05:20 в Орегоне
    schedule.every().day.at("05:20").do(main)   # ТЕСТ: 15:20 МСК
    schedule.every().day.at("00:00").do(main)   # 10:00 МСК
    schedule.every().day.at("05:00").do(main)   # 15:00 МСК
    schedule.every().day.at("09:00").do(main)   # 19:00 МСК

    print("⏰ Планировщик запущен (Орегон UTC-7)")
    print("📅 Тест в 15:20 МСК, затем 10:00, 15:00, 19:00")
    while True:
        schedule.run_pending()
        time.sleep(60)

@app.route('/')
def home():
    return "News Bot running!", 200

@app.route('/health')
def health():
    return "OK", 200

if __name__ == "__main__":
    thread = threading.Thread(target=schedule_checker)
    thread.daemon = True
    thread.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
