import requests
import os
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "-1003900711058"
NEWS_API_URL = "https://cryptocurrency.cv/api/news?lang=ru"

def fetch_news():
    try:
        r = requests.get(NEWS_API_URL, timeout=10)
        data = r.json()
        articles = data.get('articles', data.get('news', []))
        if not articles:
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
        return result
    except Exception as e:
        print(f"Ошибка: {e}")
        return []

def send_photo(chat_id, image_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        requests.post(url, json={"chat_id": chat_id, "photo": image_url, "caption": caption, "parse_mode": "Markdown"})
    except Exception as e:
        print(e)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        print(e)

def format_caption(item):
    return f"📰 *{item['title']}*\n\n{item['summary']}\n\n🔗 [Читать]({item['url']})\n---\n💡 *Alpha Trades*"

@app.route('/publish')
def publish():
    print("🔄 Публикация новостей по запросу")
    news = fetch_news()
    if not news:
        return "Нет новостей", 200
    for item in news:
        caption = format_caption(item)
        if item['image']:
            send_photo(CHANNEL_ID, item['image'], caption)
        else:
            send_message(CHANNEL_ID, caption)
    return f"Отправлено {len(news)} новостей", 200

@app.route('/')
def home():
    return "News bot ready. Use /publish to trigger", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
