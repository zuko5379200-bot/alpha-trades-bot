import os
import requests
import time

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TRADE_CHANNEL_ID = "-1003900711058"
DESIGN_CHANNEL_ID = "-1003863206770"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})
        print(f"Сообщение отправлено в {chat_id}, статус: {r.status_code}")
    except Exception as e:
        print(f"Ошибка: {e}")

print("🚀 Бот запущен в режиме polling")
print(f"🤖 Токен: {BOT_TOKEN[:10]}...")

last_update_id = 0
while True:
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update_id+1}&timeout=30"
        resp = requests.get(url, timeout=35)
        
        if resp.status_code == 200:
            updates = resp.json().get('result', [])
            for update in updates:
                last_update_id = update['update_id']
                
                if 'message' in update and 'text' in update['message']:
                    chat_id = update['message']['chat']['id']
                    text = update['message']['text'].lower()
                    print(f"📩 Получено: {text} от {chat_id}")
                    
                    if text == '/status':
                        send_message(chat_id, "✅ Бот работает! Статус: OK")
                    elif text == '/trade_post':
                        send_message(TRADE_CHANNEL_ID, "📊 Тестовый пост в трейдерский канал")
                        send_message(chat_id, "✅ Пост отправлен в трейдерский канал")
                    elif text == '/design_post':
                        send_message(DESIGN_CHANNEL_ID, "🎨 Тестовый пост в дизайн-канал")
                        send_message(chat_id, "✅ Пост отправлен в дизайн-канал")
                    else:
                        send_message(chat_id, "❓ Неизвестная команда. Доступно: /status, /trade_post, /design_post")
        else:
            print(f"Ошибка: {resp.status_code}")
    except Exception as e:
        print(f"Ошибка в цикле: {e}")
    
    time.sleep(1)
