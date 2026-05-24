import requests
import os
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "-1003900711058"

RUSSIAN_API_URL = "https://cryptocurrency.cv/api/news?lang=ru&limit=10"
ENGLISH_API_URL = "https://cryptocurrency.cv/api/news?lang=en&limit=10"

def fetch_news():
    try:
        print("🔍 Поиск русских новостей...")
        r = requests.get(RUSSIAN_API_URL, timeout=15)
        data = r.json()
        articles = data.get('articles', data.get('news', []))
        if articles:
            print(f"✅ Найдено {len(articles)} русских новостей")
            return articles[:5], 'ru'
    except Exception as e:
        print(f"Ошибка: {e}")

    try:
        print("⚠️ Загружаю английские новости...")
        r = requests.get(ENGLISH_API_URL, timeout=15)
        data = r.json()
        articles = data.get('articles', data.get('news', []))
        if articles:
            print(f"✅ Найдено {len(articles)} английских новостей")
            return articles[:5], 'en'
    except Exception as e:
        print(f"Ошибка: {e}")

    print("❌ Новостей нет")
    return [], None

def send_photo(chat_id, image_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        requests.post(url, json={"chat_id": chat_id, "photo": image_url, "caption": caption, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Ошибка фото: {e}")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Ошибка текста: {e}")

def format_caption(item, language):
    title = item.get('title', 'Новость')
    summary = (item.get('description') or '')[:300]
    url = item.get('url', '')
    return (f"📰 *{title}*\n\n{summary}\n\n🔗 [Читать]({url})\n---\n💡 *Alpha Trades*")

@app.route('/publish')
def publish():
    print("🚀 Публикация новостей")
    news, lang = fetch_news()
    if not news:
        return "Нет новостей", 200
    for item in news:
        caption = format_caption(item, lang)
        image = item.get('urlToImage') or item.get('image') or item.get('media')
        if image:
            send_photo(CHANNEL_ID, image, caption)
        else:
            send_message(CHANNEL_ID, caption)
    return f"Отправлено {len(news)} новостей", 200

@app.route('/')
def home():
    return "News bot ready", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
