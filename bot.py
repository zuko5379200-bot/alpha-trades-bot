import os
import json
import random
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "-1003900711058"
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

# Данные для GitHub Gist
GIST_TOKEN = os.environ.get("GIST_TOKEN")
GIST_ID = os.environ.get("GIST_ID")

def load_state():
    """Загружает индекс из Gist"""
    if not GIST_TOKEN or not GIST_ID:
        print("❌ GIST_TOKEN или GIST_ID не заданы")
        return -1
    try:
        url = f"https://api.github.com/gists/{GIST_ID}"
        headers = {"Authorization": f"token {GIST_TOKEN}"}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            content = data['files']['state.json']['content']
            state = json.loads(content)
            return state.get('index', -1)
    except Exception as e:
        print(f"Ошибка загрузки Gist: {e}")
    return -1

def save_state(index):
    """Сохраняет индекс в Gist"""
    if not GIST_TOKEN or not GIST_ID:
        print("❌ GIST_TOKEN или GIST_ID не заданы")
        return
    try:
        url = f"https://api.github.com/gists/{GIST_ID}"
        headers = {"Authorization": f"token {GIST_TOKEN}"}
        data = {
            "files": {
                "state.json": {
                    "content": json.dumps({"index": index}, indent=2)
                }
            }
        }
        requests.patch(url, headers=headers, json=data)
        print(f"✅ Индекс {index} сохранён в Gist")
    except Exception as e:
        print(f"Ошибка сохранения: {e}")

def load_posts():
    try:
        with open('posts.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        return [p.strip() for p in content.split('---') if p.strip()]
    except:
        return ["Тестовый пост"]

def get_image_from_pexels(keywords):
    """Ищет картинку в Pexels по ключевым словам"""
    if not PEXELS_API_KEY:
        return None
    try:
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": keywords, "per_page": 5, "orientation": "landscape"}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        if data.get('photos') and len(data['photos']) > 0:
            photo = random.choice(data['photos'])
            return photo['src']['large']
    except Exception as e:
        print(f"Ошибка Pexels: {e}")
    return None

def get_local_image():
    """Берёт случайную картинку из папки images на сервере"""
    try:
        images_dir = "images"
        if not os.path.exists(images_dir):
            print(f"📁 Папка {images_dir} не найдена на сервере")
            return None
        images = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        if images:
            selected = random.choice(images)
            print(f"🖼️ Локальная картинка: {selected}")
            return f"/{images_dir}/{selected}"
        else:
            print("⚠️ В папке images нет картинок")
    except Exception as e:
        print(f"Ошибка локальной картинки: {e}")
    return None

def extract_keywords(text):
    """Извлекает ключевые слова из текста для поиска картинки"""
    word_map = {
        'биткоин': 'bitcoin', 'btc': 'bitcoin',
        'эфир': 'ethereum', 'eth': 'ethereum',
        'трейдинг': 'trading',
        'график': 'chart',
        'прибыль': 'profit',
        'опцион': 'options',
        'рынок': 'market',
        'анализ': 'analysis',
        'стратегия': 'strategy'
    }
    text_lower = text.lower()
    keywords = [en for ru, en in word_map.items() if ru in text_lower]
    return ' '.join(keywords) if keywords else 'trading'

def send_photo(chat_id, image_url, caption):
    """Отправляет фото с подписью"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        r = requests.post(url, json={
            "chat_id": chat_id,
            "photo": image_url,
            "caption": caption,
            "parse_mode": "Markdown"
        })
        print(f"📸 Фото отправлено, статус: {r.status_code}")
        return True
    except Exception as e:
        print(f"Ошибка фото: {e}")
        return False

def send_message(chat_id, text):
    """Отправляет только текст"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        })
        print(f"💬 Текст отправлен, статус: {r.status_code}")
    except Exception as e:
        print(f"Ошибка: {e}")

@app.route('/')
def home():
    return "Bot is alive!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data or 'message' not in data:
        return "OK", 200

    chat_id = data['message']['chat']['id']
    text = data['message'].get('text', '')
    print(f"📩 Получена команда: {text} от {chat_id}")

    if text == '/start':
        send_message(chat_id, "🤖 Бот для Alpha Trades запущен!\nИспользуй /post для публикации")

    elif text == '/post':
        posts = load_posts()
        current_index = load_state()
        next_index = current_index + 1

        if next_index >= len(posts):
            send_message(chat_id, "🏁 Все посты опубликованы!")
            return "OK", 200

        post_text = posts[next_index]
        
        # 1. Пробуем найти картинку через Pexels
        keywords = extract_keywords(post_text)
        image_url = get_image_from_pexels(keywords)
        
        # 2. Если Pexels не нашёл — берём локальную картинку
        if not image_url:
            local_img = get_local_image()
            if local_img:
                base_url = "https://alpha-trades-bot.onrender.com"
                image_url = f"{base_url}{local_img}"
                print(f"🖼️ Использую локальную картинку: {image_url}")
        
        # Отправляем в канал
        if image_url:
            send_photo(CHANNEL_ID, image_url, post_text)
        else:
            send_message(CHANNEL_ID, post_text)
        
        save_state(next_index)
        send_message(chat_id, f"✅ Пост #{next_index+1} отправлен в канал!")

    elif text == '/status':
        current_index = load_state()
        posts = load_posts()
        total = len(posts)
        sent = current_index + 1
        remaining = total - sent
        send_message(chat_id, f"📊 Статистика:\nВсего: {total}\nОтправлено: {sent}\nОсталось: {remaining}")

    elif text == '/reset':
        save_state(-1)
        send_message(chat_id, "🔄 Прогресс сброшен!")

    elif text == '/help':
        send_message(chat_id, "📋 Команды:\n/start\n/post\n/status\n/reset\n/help")

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
