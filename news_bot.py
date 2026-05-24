import requests
import time
import os
import threading
from datetime import datetime
from flask import Flask

# --- Настройки ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "-1003900711058"

# 🎯 ГЛАВНОЕ ИЗМЕНЕНИЕ: Добавлен параметр lang=ru для получения новостей на русском языке
NEWS_API_URL = "https://cryptocurrency.cv/api/news?lang=ru"

app = Flask(__name__)

# --- Функции бота ---
def fetch_news():
    """Получает свежие криптоновости на русском языке"""
    try:
        print(f"[{datetime.now()}] Запрашиваю новости на русском...")
        r = requests.get(NEWS_API_URL, timeout=10)
        data = r.json()
        
        # API может возвращать список статей в поле 'articles' или 'news'
        articles = data.get('articles', data.get('news', []))
        
        if not articles:
            print("Новости не найдены.")
            return []
            
        items = articles[:5]
        result = []
        for item in items:
            result.append({
                'title': item.get('title', 'Без заголовка'),
                'source': item.get('source', {}).get('name', 'Crypto News'),
                'summary': item.get('description', '')[:300],
                'url': item.get('url', '')
            })
        print(f"Найдено {len(result)} новостей на русском")
        return result
    except Exception as e:
        print(f"Ошибка при получении новостей: {e}")
        return []

def send_message(chat_id, text):
    """Отправляет сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        })
        print(f"Статус отправки: {response.status_code}")
        if response.status_code != 200:
            print(f"Ошибка при отправке: {response.text}")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

def main():
    print(f"[{datetime.now()}] 🔄 Запуск сбора новостей...")
    news = fetch_news()
    if not news:
        print("Нет новостей для отправки.")
        return
    for i, item in enumerate(news):
        # Улучшенное форматирование поста
        post = (
            f"📰 *{item['title']}*\n\n"
            f"{item['summary']}\n\n"
            f"🔗 [Читать полностью]({item['url']})\n"
            f"---\n"
            f"💡 *Alpha Trades — трейдинг с умом*"
        )
        send_message(CHANNEL_ID, post)
        print(f"Отправлен пост {i+1}/{len(news)}: {item['title'][:50]}...")
        time.sleep(3)  # Пауза между постами
    print(f"[{datetime.now()}] ✅ Готово! Отправлено {len(news)} постов.")

def schedule_checker():
    """Функция планировщика, работает в фоновом потоке"""
    import schedule
    # Устанавливаем расписание (Московское время)
    schedule.every().day.at("10:00").do(main)
    schedule.every().day.at("15:00").do(main)
    schedule.every().day.at("19:00").do(main)
    
    print("⏰ Планировщик русскоязычных новостей запущен.")
    print("📅 Расписание публикаций: 10:00, 15:00, 19:00 по Москве")
    while True:
        schedule.run_pending()
        time.sleep(60)

# --- Веб-сервер для Render (чтобы не падал) ---
@app.route('/')
def home():
    return "News Bot (Russian) is running!", 200

@app.route('/health')
def health():
    return "OK", 200

# --- Запуск ---
if __name__ == "__main__":
    # Запускаем планировщик в отдельном потоке
    thread = threading.Thread(target=schedule_checker)
    thread.daemon = True
    thread.start()
    
    # Запускаем Flask-сервер (для порта Render)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
