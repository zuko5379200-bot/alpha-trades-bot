import requests
import os
from flask import Flask
from googletrans import Translator

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "-1003900711058"

# Основное API, русские новости
RUSSIAN_API_URL = "https://cryptocurrency.cv/api/news?lang=ru&limit=10"
# Запасное API, английские новости
ENGLISH_API_URL = "https://cryptocurrency.cv/api/news?lang=en&limit=10"

translator = Translator()

def translate_title(title):
    """Переводит заголовок с английского на русский"""
    try:
        translated = translator.translate(title, src='en', dest='ru')
        return translated.text
    except:
        return title  # Если перевод не удался, возвращаем оригинал

def fetch_news():
    # Сначала пробуем получить русские новости
    try:
        print("🔍 Поиск русских новостей...")
        r = requests.get(RUSSIAN_API_URL, timeout=15)
        data = r.json()
        articles = data.get('articles', data.get('news', []))
        if articles:
            print(f"✅ Найдено {len(articles)} русских новостей")
            return articles[:5], 'ru'
    except Exception as e:
        print(f"Ошибка при запросе русских новостей: {e}")

    # Если русских нет, берём английские и переводим заголовки
    try:
        print("⚠️ Русских новостей нет, загружаю английские...")
        r = requests.get(ENGLISH_API_URL, timeout=15)
        data = r.json()
        articles = data.get('articles', data.get('news', []))
        if articles:
            print(f"✅ Найдено {len(articles)} английских новостей (заголовки будут переведены)")
            return articles[:5], 'en'
    except Exception as e:
        print(f"Ошибка при запросе английских новостей: {e}")

    print("❌ Новостей нет ни на русском, ни на английском")
    return [], None

def send_photo(chat_id, image_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "photo": image_url, "caption": caption, "parse_mode": "Markdown"})
        print(f"Фото отправлено, статус: {r.status_code}")
    except Exception as e:
        print(f"Ошибка фото: {e}")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
        print(f"Текст отправлен, статус: {r.status_code}")
    except Exception as e:
        print(f"Ошибка текста: {e}")

def format_caption(item, language):
    """Форматирует пост. Если язык английский — переводит заголовок"""
    title = item.get('title', 'Новость')
    if language == 'en':
        title = translate_title(title)
        title = f"🌐 {title}"  # Добавляем значок, что новость переведена

    summary = (item.get('description') or '')[:300]
    url = item.get('url', '')
    
    return (f"📰 *{title}*\n\n"
            f"{summary}\n\n"
            f"🔗 [Читать полностью]({url})\n"
            f"---\n"
            f"💡 *Alpha Trades*")

@app.route('/publish')
def publish():
    print("🔄 Публикация новостей по запросу")
    news_articles, language = fetch_news()
    
    if not news_articles:
        return "Нет новостей для публикации", 200

    for item in news_articles:
        caption = format_caption(item, language)
        image = item.get('urlToImage') or item.get('image') or item.get('media')
        
        if image:
            send_photo(CHANNEL_ID, image, caption)
        else:
            send_message(CHANNEL_ID, caption)
    
    return f"Отправлено {len(news_articles)} новостей (источник: {'русский' if language == 'ru' else 'английский + перевод'})", 200

@app.route('/')
def home():
    return "News bot ready. Use /publish to trigger", 200

if __name__ == "__main__":
    # Установим модуль для перевода (если его нет, он установится автоматически при первом запуске)
    try:
        import googletrans
    except ImportError:
        import subprocess
        subprocess.run(['pip', 'install', 'googletrans==4.0.0-rc1'])
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
