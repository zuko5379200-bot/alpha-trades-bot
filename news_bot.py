import requests
import time
import os
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "-1003900711058"

NEWS_API_URL = "https://cryptocurrency.cv/api/news"

def fetch_news():
    try:
        r = requests.get(NEWS_API_URL)
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
        print(f"Ошибка: {e}")
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
        print(e)

def main():
    print(f"[{datetime.now()}] Сбор новостей...")
    news = fetch_news()
    for item in news:
        post = f"📰 *{item['title']}*\n\n{item['summary']}\n\n🔗 [Читать]({item['url']})"
        send_message(CHANNEL_ID, post)
        time.sleep(3)

if __name__ == "__main__":
    import schedule
    schedule.every().day.at("10:00").do(main)
    schedule.every().day.at("15:00").do(main)
    schedule.every().day.at("19:00").do(main)

    while True:
        schedule.run_pending()
        time.sleep(60)
