import os
import json
from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "-3900711058"

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
        return ["Тестовый пост 1", "Тестовый пост 2"]

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={"chat_id": chat_id, "text": text})
        print(f"DEBUG: Отправка в {chat_id}, статус: {response.status_code}")
        print(f"DEBUG: Ответ Telegram: {response.text}")
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

        send_message(CHANNEL_ID, posts[next_idx])
        state['index'] = next_idx
        save_state(state)
        send_message(chat_id, f"✅ Пост #{next_idx+1} отправлен в канал!")

    elif text == '/reset':
        save_state({"index": -1})
        send_message(chat_id, "🔄 Прогресс сброшен!")

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))    elif text == '/reset':
        save_state({"index": -1})
        send_message(chat_id, "🔄 Прогресс сброшен!")

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
