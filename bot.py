import os
import json
import random
import requests
from deep_translator import GoogleTranslator
import xml.etree.ElementTree as ET
import time

# ========== ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
GIST_TOKEN = os.environ.get("GIST_TOKEN")
TRADE_GIST_ID = os.environ.get("TRADE_GIST_ID")
DESIGN_GIST_ID = "5f05dbf02309981cdb6253d8726e23fd"

# ========== КАНАЛЫ ==========
TRADE_CHANNEL_ID = "-1003900711058"
DESIGN_CHANNEL_ID = "-1003863206770"

# ========== ПОДПИСИ ==========
TRADE_SIGNATURE = "\n\n📊 Alpha Trades | Трейдинг без эмоций"
DESIGN_SIGNATURE = "\n\n✨ Александр Немцев | Веб-дизайн"

# ========== RSS ДЛЯ НОВОСТЕЙ ДИЗАЙНА ==========
DESIGN_RSS_FEEDS = [
    "https://habr.com/ru/rss/hub/web_design/all/?fl=ru",
    "https://vc.ru/rss/all?tag=web-design"
]

# ========== 180 СОВЕТОВ ДЛЯ ДИЗАЙНА ==========
DESIGN_TIPS = [
    "🔥 Используй отступы (padding) — они важнее, чем кажется. 20px вокруг текста спасают дизайн.",
    "🎨 Не больше 3 шрифтов на сайте. Лучше 2: один для заголовков, второй для текста.",
    "🖼️ Не растягивай логотип на весь экран. Оставь место для воздуха.",
    "📱 Сначала дизайн для мобильных. Потом для десктопа.",
    "⚡ Анимация не должна длиться дольше 300 мс.",
    "🎯 Кнопка CTA должна быть яркой и заметной.",
    "📐 Сетка в Figma — твой лучший друг.",
    "🖱️ Кнопка должна менять вид при наведении.",
    "📊 95% пользователей не скроллят дальше первого экрана.",
    "🌈 Не используй больше 5 цветов на сайте.",
]

# ========== НАСТРОЙКИ ДЛЯ НОВОСТЕЙ ТРЕЙДИНГА ==========
RUSSIAN_API_URL = "https://cryptocurrency.cv/api/news?lang=ru&limit=10"
ENGLISH_API_URL = "https://cryptocurrency.cv/api/news?lang=en&limit=10"

translator = GoogleTranslator(source='en', target='ru')

# ========== ОБЩИЕ ФУНКЦИИ ==========

def load_trade_state():
    if not GIST_TOKEN or not TRADE_GIST_ID:
        return 0
    try:
        url = f"https://api.github.com/gists/{TRADE_GIST_ID}"
        headers = {"Authorization": f"token {GIST_TOKEN}"}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            content = data['files']['state.json']['content']
            state = json.loads(content)
            return state.get('index', 0)
    except Exception as e:
        print(f"Ошибка загрузки Gist: {e}")
    return 0

def save_trade_state(index):
    if not GIST_TOKEN or not TRADE_GIST_ID:
        return
    try:
        url = f"https://api.github.com/gists/{TRADE_GIST_ID}"
        headers = {"Authorization": f"token {GIST_TOKEN}"}
        data = {
            "files": {
                "state.json": {
                    "content": json.dumps({"index": index}, indent=2)
                }
            }
        }
        requests.patch(url, headers=headers, json=data)
        print(f"✅ Индекс трейдинга {index} сохранён")
    except Exception as e:
        print(f"Ошибка сохранения: {e}")

def load_design_state():
    if not GIST_TOKEN or not DESIGN_GIST_ID:
        return 0
    try:
        url = f"https://api.github.com/gists/{DESIGN_GIST_ID}"
        headers = {"Authorization": f"token {GIST_TOKEN}"}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            content = data['files']['progress.json']['content']
            state = json.loads(content)
            return state.get('last_post_index', 0)
    except Exception as e:
        print(f"Ошибка загрузки Gist дизайна: {e}")
    return 0

def save_design_state(index):
    if not GIST_TOKEN or not DESIGN_GIST_ID:
        return
    try:
        url = f"https://api.github.com/gists/{DESIGN_GIST_ID}"
        headers = {"Authorization": f"token {GIST_TOKEN}"}
        data = {
            "files": {
                "progress.json": {
                    "content": json.dumps({"last_post_index": index}, indent=2)
                }
            }
        }
        requests.patch(url, headers=headers, json=data)
        print(f"✅ Индекс дизайна {index} сохранён")
    except Exception as e:
        print(f"Ошибка сохранения: {e}")

def load_trade_posts():
    try:
        with open('posts.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        return [p.strip() for p in content.split('---') if p.strip()]
    except:
        return ["Тестовый пост по трейдингу"]

def get_image_from_pexels(keywords):
    if not PEXELS_API_KEY:
        return None
    try:
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": keywords, "per_page": 5, "orientation": "landscape"}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        if data.get('photos'):
            photo = random.choice(data['photos'])
            return photo['src']['large']
    except Exception as e:
        print(f"Ошибка Pexels: {e}")
    return None

def send_photo(chat_id, image_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        r = requests.post(url, json={
            "chat_id": chat_id,
            "photo": image_url,
            "caption": caption,
            "parse_mode": "HTML"
        })
        return r.status_code == 200
    except Exception as e:
        print(f"Ошибка фото: {e}")
        return False

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})
    except Exception as e:
        print(f"Ошибка: {e}")

# ========== НОВОСТИ ТРЕЙДИНГА ==========

def translate_title(title):
    try:
        return translator.translate(title)
    except:
        return title

def fetch_trade_news():
    try:
        r = requests.get(RUSSIAN_API_URL, timeout=15)
        data = r.json()
        articles = data.get('articles', data.get('news', []))
        if articles:
            return articles[:5], 'ru'
    except:
        pass
    try:
        r = requests.get(ENGLISH_API_URL, timeout=15)
        data = r.json()
        articles = data.get('articles', data.get('news', []))
        if articles:
            return articles[:5], 'en'
    except:
        pass
    return [], None

def format_news_caption(item, language):
    title = item.get('title', 'Новость')
    if language == 'en':
        title = translate_title(title)
        title = f"🌐 {title}"
    summary = (item.get('description') or '')[:300]
    url = item.get('url', '')
    return f"📰 <b>{title}</b>\n\n{summary}\n\n🔗 <a href='{url}'>Читать</a>\n---\n💡 Alpha Trades"

def cmd_trade_news(chat_id):
    send_message(chat_id, "📡 Загружаю новости...")
    news, lang = fetch_trade_news()
    if not news:
        send_message(chat_id, "❌ Новостей сейчас нет.")
        return
    for item in news:
        caption = format_news_caption(item, lang)
        image = item.get('urlToImage') or item.get('image')
        if image:
            send_photo(TRADE_CHANNEL_ID, image, caption)
        else:
            send_message(TRADE_CHANNEL_ID, caption)
    send_message(chat_id, f"✅ Отправлено {len(news)} новостей")

# ========== НОВОСТИ ДИЗАЙНА ==========

def parse_rss(url):
    try:
        response = requests.get(url, timeout=15)
        root = ET.fromstring(response.content)
        items = root.findall('.//item')
        if not items:
            items = root.findall('.//{http://www.w3.org/2005/Atom}entry')
        news = []
        for item in items[:2]:
            title_elem = item.find('title')
            link_elem = item.find('link')
            if title_elem is not None and title_elem.text:
                title = title_elem.text
                link = link_elem.text if link_elem is not None else '#'
                if any(ord(c) < 128 for c in title) and len(title) > 10:
                    try:
                        title = translator.translate(title)
                    except:
                        pass
                news.append({"title": title, "link": link})
        return news
    except Exception as e:
        print(f"Ошибка RSS: {e}")
        return []

def fetch_design_news():
    all_news = []
    for feed_url in DESIGN_RSS_FEEDS:
        all_news.extend(parse_rss(feed_url))
    unique = []
    seen = set()
    for item in all_news:
        if item['link'] not in seen:
            unique.append(item)
            seen.add(item['link'])
    return unique[:5]

def cmd_design_news(chat_id):
    send_message(chat_id, "📡 Загружаю новости дизайна...")
    news = fetch_design_news()
    if not news:
        send_message(chat_id, "❌ Новостей дизайна сейчас нет.")
        return
    msg = "📰 <b>Новости веб-дизайна</b>\n\n"
    for item in news:
        msg += f"🔹 <a href='{item['link']}'>{item['title']}</a>\n"
    send_message(DESIGN_CHANNEL_ID, msg)
    send_message(chat_id, f"✅ Отправлено {len(news)} новостей дизайна")

# ========== КОМАНДЫ ==========

def cmd_trade_post(chat_id):
    posts = load_trade_posts()
    current_index = load_trade_state()
    if current_index >= len(posts):
        send_message(chat_id, "🏁 Все посты трейдинга опубликованы!")
        return
    post_text = posts[current_index] + TRADE_SIGNATURE
    keywords = 'trading'
    image_url = get_image_from_pexels(keywords)
    if image_url:
        send_photo(TRADE_CHANNEL_ID, image_url, post_text)
    else:
        send_message(TRADE_CHANNEL_ID, post_text)
    save_trade_state(current_index + 1)
    send_message(chat_id, f"✅ Пост трейдинг #{current_index+1} отправлен!")

def cmd_trade_status(chat_id):
    current_index = load_trade_state()
    posts = load_trade_posts()
    total = len(posts)
    sent = current_index
    remaining = total - sent
    send_message(chat_id, f"📊 Трейдинг:\nВсего: {total}\nОтправлено: {sent}\nОсталось: {remaining}")

def cmd_trade_reset(chat_id):
    save_trade_state(0)
    send_message(chat_id, "🔄 Прогресс трейдинга сброшен!")

def cmd_design_post(chat_id):
    current_index = load_design_state()
    if current_index >= len(DESIGN_TIPS):
        send_message(chat_id, "🏁 Все советы дизайна опубликованы!")
        return
    post_text = DESIGN_TIPS[current_index] + DESIGN_SIGNATURE
    image_url = get_image_from_pexels('web design')
    if image_url:
        send_photo(DESIGN_CHANNEL_ID, image_url, post_text)
    else:
        send_message(DESIGN_CHANNEL_ID, post_text)
    save_design_state(current_index + 1)
    send_message(chat_id, f"✅ Пост дизайн #{current_index+1} отправлен!")

def cmd_design_status(chat_id):
    current_index = load_design_state()
    total = len(DESIGN_TIPS)
    sent = current_index
    remaining = total - sent
    send_message(chat_id, f"🎨 Дизайн:\nВсего: {total}\nОтправлено: {sent}\nОсталось: {remaining}")

def cmd_design_reset(chat_id):
    save_design_state(0)
    send_message(chat_id, "🔄 Прогресс дизайна сброшен!")

def cmd_status(chat_id):
    cmd_trade_status(chat_id)
    cmd_design_status(chat_id)

def cmd_help(chat_id):
    help_text = """
🤖 <b>Универсальный бот</b>

<b>Трейдинг:</b>
/trade_post — следующий пост
/trade_news — новости
/trade_status — прогресс
/trade_reset — сброс

<b>Дизайн:</b>
/design_post — совет
/design_news — новости
/design_status — прогресс
/design_reset — сброс

<b>Общее:</b>
/status — оба прогресса
/help — справка
"""
    send_message(chat_id, help_text)

# ========== POLLING ==========
print("🚀 Полная версия бота запущена в режиме polling")
print(f"🤖 Токен: {BOT_TOKEN[:15] if BOT_TOKEN else 'не найден'}...")

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
                    print(f"📩 Получена команда: {text}")
                    
                    if text == '/status':
                        cmd_status(chat_id)
                    elif text == '/trade_post':
                        cmd_trade_post(chat_id)
                    elif text == '/design_post':
                        cmd_design_post(chat_id)
                    elif text == '/trade_news':
                        cmd_trade_news(chat_id)
                    elif text == '/design_news':
                        cmd_design_news(chat_id)
                    elif text == '/trade_status':
                        cmd_trade_status(chat_id)
                    elif text == '/design_status':
                        cmd_design_status(chat_id)
                    elif text == '/trade_reset':
                        cmd_trade_reset(chat_id)
                    elif text == '/design_reset':
                        cmd_design_reset(chat_id)
                    elif text == '/help':
                        cmd_help(chat_id)
                    elif text == '/start':
                        send_message(chat_id, "🤖 Бот работает. Команды: /help")
                    else:
                        send_message(chat_id, "❓ Неизвестная команда. Напиши /help")
    except Exception as e:
        print(f"Ошибка: {e}")
    time.sleep(1)
