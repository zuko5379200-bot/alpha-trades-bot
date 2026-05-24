import os
import json
import random
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "-1003900711058"
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

def load_state():
    try:
        with open('state.json', 'r') as f:
            return json.load(f)
    except:
        return {"index": -1}

def save_state(data):
    with open('state.json', 'w') as f:
        json.dump(data, f)

def load_posts():
    try:
        with open('posts.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        return [p.strip() for p in content.split('---') if p.strip()]
    except:
        return ["Тестовый пост"]

def get_image_from_pexels(keywords):
    print(f"DEBUG: Ищу картинку в Pexels по запросу: {keywords}")
    if not PEXELS_API_KEY:
        print("DEBUG: PEXELS_API_KEY не найден в окружении")
        return None
    try:
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": keywords, "per_page": 5, "orientation": "landscape"}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"DEBUG: Pexels ответил со статусом: {response.status_code}")
        data = response.json()
        if data.get('photos') and len(data['photos']) > 0:
            photo = random.choice(data['photos'])
            print(f"DEBUG: Нашёл картинку: {photo['src']['large'][:50]}...")
            return photo['src']['large']
        print("DEBUG: Pexels не нашёл картинок")
        return None
    except Exception as e:
        print(f"Ошибка Pexels: {e}")
        return None

def get_local_image():
    try:
        images_dir = "images"
        if not os.path.exists(images_dir):
            return None
        images = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        if images:
            return f"/{images_dir}/{random.choice(images)}"
        return None
    except Exception as e:
        print(f"Ошибка локальной картинки: {e}")
        return None

def extract_keywords(text):
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
    result = ' '.join(keywords) if keywords else 'trading'
    print(f"DEBUG: Из текста извлёк ключевые слова: {result}")
    return result

def send_photo_with_caption(chat_id, image_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        response = requests.post(url, json={"chat_id": chat_id, "photo": image_url, "caption": caption, "parse_mode": "Markdown"})
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка отправки фото: {e}")
        return False

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

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
    print(f"DEBUG: Получена команда: {text} от {chat_id}")

    if text == '/start':
        send_message(chat_id, "🤖 Бот для Alpha Trades запущен!\nИспользуй /post для публикации")

    elif text == '/post':
        posts = load_posts()
        state = load_state()
        next_idx = state['index'] + 1
        if next_idx >= len(posts):
            send_message(chat_id, "🏁 Все посты опубликованы!")
            return "OK", 200

        post_text = posts[next_idx]
        keywords = extract_keywords(post_text)
        image_url = get_image_from_pexels(keywords)
        if not image_url:
            local_img = get_local_image()
            if local_img:
                base_url = "https://alpha-trades-bot.onrender.com"
                image_url = f"{base_url}{local_img}"
                print(f"DEBUG: Использую локальную картинку: {image_url}")

        if image_url:
            send_photo_with_caption(CHANNEL_ID, image_url, post_text)
        else:
            print("DEBUG: Картинка не найдена, отправляю только текст")
            send_message(CHANNEL_ID, post_text)

        state['index'] = next_idx
        save_state(state)
        send_message(chat_id, f"✅ Пост #{next_idx+1} отправлен в канал!")

    elif text == '/status':
        posts = load_posts()
        state = load_state()
        total = len(posts)
        sent = state['index'] + 1
        remaining = total - sent
        send_message(chat_id, f"📊 Статистика:\nВсего: {total}\nОтправлено: {sent}\nОсталось: {remaining}")

    elif text == '/reset':
        save_state({"index": -1})
        send_message(chat_id, "🔄 Прогресс сброшен!")

    elif text == '/help':
        send_message(chat_id, "📋 Команды:\n/start\n/post\n/status\n/reset\n/help")

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
