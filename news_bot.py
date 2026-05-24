import requests
import time
import os
import threading
from datetime import datetime
from flask import Flask

# --- Настройки ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "-1003900711058"

# API для новостей на русском с картинками
NEWS_API_URL = "https://cryptocurrency.cv/api/news?lang=ru"

app = Flask(__name__)

def fetch_news():
    """Получает свежие криптоновости на русском языке с картинками"""
    try:
        print(f"[{datetime.now()}] Запрашиваю новости на русском...")
        r = requests.get(NEWS_API_URL, timeout=10)
        data = r.json()
        
        # API может возвращать список в поле 'articles' или 'news'
        articles = data.get('articles', data.get('news', []))
        
        if not articles:
            print("Новости не найдены.")
            return []
            
        items = articles[:5]  # Берём 5 самых свежих
        result = []
        for item in items:
            # Извлекаем URL картинки (если есть)
            image_url = None
            
            # Пробуем разные поля, где может быть картинка
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
        print(f"Найдено {len(result)} новостей на русском")
        return result
    except Exception as e:
        print(f"Ошибка при получении новостей: {e}")
        return []

def send_photo_with_caption(chat_id, image_url, caption):
    """Отправляет фото с подписью"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        response = requests.post(url, json={
            "chat_id": chat_id,
            "photo": image_url,
            "caption": caption,
            "parse_mode": "Markdown"
        })
        print(f"Отправка фото, статус: {response.status_code}")
        if response.status_code != 200:
            print(f"Ошибка: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка при отправке фото: {e}")
        return False

def send_message(chat_id, text):
    """Отправляет только текст (если нет картинки)"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        })
        print(f"Отправка текста, статус: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return False

def format_caption(news_item):
    """Форматирует текст для подписи к картинке"""
    caption = (
        f"📰 *{news_item['title']}*\n\n"
        f"{news_item['summary']}\n\n"
        f"🔗 [Читать полностью]({news_item['url']})\n"
        f"---\n"
        f"💡 *Alpha Trades — трейдинг с умом*"
    )
    return caption

def main():
    print(f"[{datetime.now()}] 🔄 Запуск сбора новостей...")
    news = fetch_news()
    if not news:
        print("Нет новостей для отправки.")
        return
    
    for i, item in enumerate(news):
        caption = format_caption(item)
        
        # Если есть картинка — отправляем с фото
        if item['image']:
            print(f"Отправляю пост {i+1}/{len(news)} с картинкой: {item['title'][:50]}...")
            success = send_photo_with_caption(CHANNEL_ID, item['image'], caption)
            # Если картинка не отправилась (битая ссылка), отправляем текстом
            if not success:
                send_message(CHANNEL_ID, caption)
        else:
            # Нет картинки — отправляем только текст
            print(f"Отправляю пост {i+1}/{len(news)} (без картинки): {item['title'][:50]}...")
            send_message(CHANNEL_ID, caption)
        
        time.sleep(3)  # Пауза между постами
    
    print(f"[{datetime.now()}] ✅ Готово! Отправлено {len(news)} постов.")

def schedule_checker():
    """Функция планировщика, работает в фоновом потоке"""
    import schedule
    # Устанавливаем расписание (Московское время)
    schedule.every().day.at("10:00").do(main)
    schedule.every().day.at("15:00").do(main)
    schedule.every().day.at("19:00").do(main)
    
    print("⏰ Планировщик запущен.")
    print("📅 Расписание: 10:00, 15:00, 19:00 по Москве")
    print("🖼️ Посты будут отправляться с картинками (если доступны)")
    while True:
        schedule.run_pending()
        time.sleep(60)

# --- Веб-сервер для Render ---
@app.route('/')
def home():
    return "News Bot with images is running!", 200

@app.route('/health')
def health():
    return "OK", 200

# --- Запуск ---
if __name__ == "__main__":
    # Запускаем планировщик в отдельном потоке
    thread = threading.Thread(target=schedule_checker)
    thread.daemon = True
    thread.start()
    
    # Запускаем Flask-сервер
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
