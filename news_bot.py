import requests
import time
import os
import threading
from datetime import datetime
from flask import Flask

os.environ['TZ'] = 'Europe/Moscow'
time.tzset()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "-1003900711058"
NEWS_API_URL = "https://cryptocurrency.cv/api/news?lang=ru"

app = Flask(__name__)

def fetch_news():
    try:
        print(f"[{datetime.now()}] Запрашиваю новости...")
        r = requests.get(NEWS_API_URL, timeout=10)
        data = r.json()
        articles = data.get('articles', data.get('news', []))
        if not articles:
            print("Новостей нет")
            return []
        result = []
        for item in articles[:5]:
            image = item.get('urlToImage') or item.get('image') or item.get('media')
            result.append({
                'title': item.get('title', 'Новость'),
                'summary': (item.get('description') or '')[:300],
                'url': item.get('url', ''),
                'image': image
            })
        print(f"Найдено {len(result)} новостей")
        return result
    except Exception as e:
        print(f"Ошибка: {e}")
        return []

def send_photo(chat_id, image_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "photo": image_url, "caption": caption, "parse_mode": "Markdown"})
        print(f"Фото отправлено, статус: {r.status_code}")
    except Exception as e:
        print(f"Ошибка фото: {e}")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
        print(f"Текст отправлен, статус: {r.status_code}")
    except Exception as e:
        print(f"Ошибка текста: {e}")

def format_caption(item):
    return f"📰 *{item['title']}*\n\n{item['summary']}\n\n🔗 [Читать]({item['url']})\n---\n💡 *Alpha Trades*"

def main():
    print(f"[{datetime.now()}] 🔄 СБОР НОВОСТЕЙ СТАРТ")
    news = fetch_news()
    if not news:
        print("Нет новостей для отправки")
        return
    for i, item in enumerate(news):
        print(f"Отправляю пост {i+1}/{len(news)}")
        caption = format_caption(item)
        if item['image']:
            send_photo(CHANNEL_ID, item['image'], caption)
        else:
            send_message(CHANNEL_ID, caption)
        time.sleep(3)
    print(f"[{datetime.now()}] ✅ ГОТОВО - отправлено {len(news)} постов")

def schedule_loop():
    print("⏰ Планировщик запущен")
    print("📅 Тест: отправка через 5 секунд")
    time.sleep(5)
    main()

@app.route('/')
def home():
    return "News bot running (MSK timezone)", 200

if __name__ == "__main__":
    thread = threading.Thread(target=schedule_loop)
    thread.daemon = True
    thread.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
