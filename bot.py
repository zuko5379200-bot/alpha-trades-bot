import os
import json
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "-1003900711058"

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
        else:
            print(f"Ошибка загрузки Gist: {r.status_code}")
    except Exception as e:
        print(f"Ошибка: {e}")
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
        r = requests.patch(url, headers=headers, json=data)
        print(f"Сохранение индекса {index}, статус: {r.status_code}")
    except Exception as e:
        print(f"Ошибка сохранения: {e}")

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
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
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

    if text == '/start':
        send_message(chat_id, "🤖 Бот для Alpha Trades запущен!\nИспользуй /post для публикации")

    elif text == '/post':
        posts = load_posts()
        current_index = load_state()
        next_index = current_index + 1

        if next_index >= len(posts):
            send_message(chat_id, "🏁 Все посты опубликованы!")
            return "OK", 200

        send_message(CHANNEL_ID, posts[next_index])
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
