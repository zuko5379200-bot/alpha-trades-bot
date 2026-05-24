import requests
import os
from flask import Flask
from deep_translator import GoogleTranslator

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "-1003900711058"

RUSSIAN_API_URL = "https://cryptocurrency.cv/api/news?lang=ru&limit=10"
ENGLISH_API_URL = "https://cryptocurrency.cv/api/news?lang=en&limit=10"

translator = GoogleTranslator(source='en', target='ru')

def translate_title(title):
    try:
        return translator.translate(title)
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return title

def fetch_news():
    try:
        print("🔍 Поиск русских новостей...")
        r = requests.get(RUSSIAN_API_URL, timeout=15)
        print(f"📡 Статус API (рус): {r.status_code}")
        data = r.json()
        articles = data.get('articles', data.get('news', []))
        if articles:
            print(f"✅ Найдено {len(articles)} русских новостей")
            return articles[:5], 'ru'
        else:
            print("⚠️ Русских новостей нет")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    try:
        print("🔍 Загружаю английские новости с переводом...")
        r = requests.get(ENGLISH_API_URL, timeout=15)
        print(f"📡 Статус API (англ): {r.status_code}")
        data = r.json()
        articles = data.get('articles', data.get('news', []))
        if articles:
            print(f"✅ Найдено {len(articles)} английских новостей (заголовки будут переведены)")
            return articles[:5], 'en'
        else:
            print("⚠️ Английских новостей нет")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    print("❌ Новостей нет")
    return [], None

def send_photo(chat_id, image_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "photo": image_url, "caption": caption, "parse_mode": "Markdown"})
        print(f"📸 Фото отправлено, статус: {r.status_code}")
    except Exception as e:
        print(f"❌ Ошибка фото: {e}")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
        print(f"💬 Текст отправлен, статус: {r.status_code}")
    except Exception as e:
        print(f"❌ Ошибка текста: {e}")

def format_caption(item, language):
    title = item.get('title', 'Новость')
    if language == 'en':
        title = translate_title(title)
        title = f"🌐 {title}"
    summary = (item.get('description') or '')[:300]
    url = item.get('url', '')
    return (f"📰 *{title}*\n\n{summary}\n\n🔗 [Читать]({url})\n---\n💡 *Alpha Trades*")

@app.route('/publish')
def publish():
    print("🚀 Публикация новостей с переводом")
    news, lang = fetch_news()
    if not news:
        return "Нет новостей", 200
    print(f"📦 Отправляю {len(news)} новостей")
    for item in news:
        caption = format_caption(item, lang)
        image = item.get('urlToImage') or item.get('image') or item.get('media')
        if image:
            send_photo(CHANNEL_ID, image, caption)
        else:
            send_message(CHANNEL_ID, caption)
    print("✅ Публикация завершена")
    return f"Отправлено {len(news)} новостей (источник: {'русский' if lang == 'ru' else 'английский + перевод'})", 200

@app.route('/')
def home():
    return "News bot ready. Use /publish to trigger", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
