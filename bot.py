import os
import json
import random
import requests
from flask import Flask, request
from deep_translator import GoogleTranslator
import xml.etree.ElementTree as ET

app = Flask(__name__)

# ========== ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
GIST_TOKEN = os.environ.get("GIST_TOKEN")
TRADE_GIST_ID = os.environ.get("TRADE_GIST_ID")
DESIGN_GIST_ID = "5f05dbf02309981cdb6253d8726e23fd"  # твой ID

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
    "📱 Сначала дизайн для мобильных. Потом для десктопа. (Mobile First)",
    "⚡ Анимация не должна длиться дольше 300 мс. Быстрее = лучше.",
    "🎯 Кнопка CTA должна быть яркой и заметной с первого взгляда.",
    "📐 Сетка (Grid) в Figma — твой лучший друг.",
    "🖱️ Кнопка должна менять вид при наведении (hover).",
    "📊 95% пользователей не скроллят дальше первого экрана, если их не зацепить.",
    "🌈 Не используй больше 5 цветов на сайте. 3 основных + 2 акцентных.",
    "📝 Текст на кнопке должен говорить о действии: 'Скачать', а не 'Нажми тут'.",
    "🎬 Видео на фоне — круто, но добавляй затемнение, чтобы текст читался.",
    "🔍 Поля ввода делай высотой 48px — золотой стандарт.",
    "📱 Шрифт на мобильных не меньше 16px.",
    "🎯 Один экран — одна цель. Не мешай регистрацию и каталог.",
    "🧩 Используй компоненты в Figma — экономит часы.",
    "⚡ Оптимизируй картинки. WebP вместо PNG.",
    "📐 Высота строки 1.5 для текста — читается легче всего.",
    "🎨 Контрастность текста и фона — проверяй через WebAIM.",
    "🖼️ Иконки должны быть из одного набора, не мешай стили.",
    "📱 Таргет для пальца — минимум 44×44 px.",
    "🧩 Не скрывай навигацию. Гамбургер-меню снижает конверсию.",
    "⚡ Скорость загрузки — часть дизайна. Проверяй через PageSpeed.",
    "🎯 Хлебные крошки (breadcrumbs) для сайтов с каталогом.",
    "📊 Формы: меньше полей = больше конверсий.",
    "🎨 Тени (box-shadow) добавляют глубину. Но не перебарщивай.",
    "📱 Адаптив: проверяй на реальных устройствах, не только в эмуляторе.",
    "🧩 Пустые состояния (empty states) — тоже дизайн.",
    "⚡ Скелетоны вместо спиннеров — пользователь чувствует прогресс.",
    "🎯 Закон Фиттса: большие кнопки ближе к курсору.",
    "📐 Правило третей в композиции.",
    "🎨 Используй готовые UI Kit'и для прототипов, не изобретай велосипед.",
    "📱 Тильда: не ставь анимацию на каждый блок. Точечно.",
    "🧩 Автолейаут в Figma — с ним макеты не разъезжаются.",
    "⚡ Не грузи шрифты всех начертаний. Только нужные.",
    "🎯 Форма подписки — предложи бонус: PDF, чек-лист, скидку.",
    "📊 Тепловые карты покажут, куда пользователь не кликает.",
    "🎨 Градиенты возвращаются. Мягкие переходы вместо плоских цветов.",
    "📱 Микроанимация на кнопках повышает доверие.",
    "🧩 Модальные окна — бесит. Используй только для критических действий.",
    "⚡ LCP (Largest Contentful Paint) — главная картинка должна грузиться быстро.",
    "🎯 Цвет ссылки должен отличаться от обычного текста.",
    "📐 Маржины и паддинги — дай элементам дышать.",
    "🎨 Неоновые акценты на тёмном фоне — тренд 2025.",
    "📱 Тильда Zero Block — полная свобода. Но не увлекайся.",
    "🧩 Сетка 12 колонок — стандарт для веба.",
    "⚡ Настрой 301 редиректы при смене URL.",
    "🎯 Тег H1 — один на страницу. Не повторяй.",
    "📊 Альт-тексты для картинок — для SEO и доступности.",
    "🎨 Брендбук: сохрани цвета, шрифты, отступы в Figma.",
    "📱 Чек-лист перед сдачей: ссылки работают, формы отправляются.",
    "🧩 Попроси друга потестировать. Свежий взгляд найдёт баги.",
    "⚡ Google Fonts подключай с preconnect для скорости.",
    "🎯 Кнопка 'Наверх' помогает на длинных страницах.",
    "📊 Аналитика: установи Яндекс.Метрику в первый же день.",
    "🎨 Закруглённые углы выглядят дружелюбнее.",
    "📱 Выравнивание по центру для коротких текстов, по левой — для длинных.",
    "🧩 Паттерн 'Z-образное сканирование' для лендингов.",
    "⚡ Используй lazy load для картинок ниже сгиба.",
    "🎯 Favicon не забывай. Профессионально выглядят с иконкой.",
    "📊 Тест с 5 пользователями найдёт 80% проблем.",
    "🎨 Минимализм — не значит пусто. Достаточно воздуха между блоками.",
    "📱 Тильда: используй 'нулевой блок' для уникальных секций.",
    "🧩 Копирайтинг на кнопках: 'Получить бесплатно' лучше 'Отправить'.",
    "⚡ WebP и AVIF — форматы будущего для изображений.",
    "🎯 Прогресс-бар в многостраничных формах снижает уходы.",
    "📊 Карта кликов покажет, куда пользователь жмёт интуитивно.",
    "🎨 Используй системные шрифты для текста (Inter, Roboto, SF).",
    "📱 Жирность шрифта: 400 для текста, 600-700 для заголовков.",
    "🧩 Настрой Open Graph для соцсетей — ссылка будет с красивой картинкой.",
    "⚡ Критический CSS — в <head>, остальное подгрузи.",
    "🎯 Чёткий визуальный иерархия: заголовок → подзаголовок → текст.",
    "📊 A/B тестируй кнопки, цвета, тексты.",
    "🎨 Свайп-галерея на мобильных вместо точек.",
    "📱 Всплывающие подсказки (tooltip) для сложных полей формы.",
    "🧩 Дизайн-система: сохраняй стили в Figma для переиспользования.",
    "⚡ Не блокируй рендеринг большими JS-файлами.",
    "🎯 Промокод при регистрации — повышает конверсию.",
    "📊 Следи за процентовкой скролла на сайте.",
    "🎨 Акцентный цвет должен быть один. Не радуга.",
    "📱 Тильда: видео из YouTube вместо загруженного файла — быстрее.",
    "🧩 Состояния кнопок: обычный, наведение, нажатие, disabled.",
    "⚡ Респонсив таблицы: горизонтальный скролл или адаптив в карточки.",
    "🎯 Выпадающие списки (dropdown) для многих вариантов.",
    "📊 Поведение пользователей: зри в корень аналитики.",
    "🎨 Плавный скролл по якорям — улучшает впечатление.",
    "📱 Не используй карусель с авто-прокруткой. Пользователь не успевает прочитать.",
    "🧩 Дизайн для леворуких — размещай главные кнопки и справа и слева.",
    "⚡ Service Worker для офлайн-режима и кэша.",
    "🎯 Автофокус в первое поле формы — маленькая, но полезная деталь.",
    "📊 Сессии пользователей: смотри, где уходят.",
    "🎨 Картинки с лицами привлекают внимание.",
    "📱 Тильда: экспорт в HTML для размещения на своём хостинге.",
    "🧩 Палитра: используй генераторы типа Coolors.co.",
    "⚡ Прелоадер для тяжёлых страниц.",
    "🎯 Кнопка 'Поделиться' в соцсети — бесплатный трафик.",
    "📊 Google Search Console покажет ошибки индексации.",
    "🎨 Иммерсивный дизайн: видео, параллакс, интерактив.",
    "📱 Не злоупотребляй поп-апами при входе на сайт.",
    "🧩 Стилизация чекбоксов и радиокнопок в духе бренда.",
    "⚡ Инлайн-валидация формы (проверка по мере ввода).",
    "🎯 Чёткий путь конверсии: от входа до целевого действия.",
    "📊 Воронка в аналитике — где утекают пользователи.",
    "🎨 Тильда: используй готовые блоки, не строй всё с нуля.",
    "📱 Анимация появления при скролле — аккуратно, не всё сразу.",
    "🧩 Маржины вертикальные и горизонтальные — поддерживай ритм.",
    "⚡ Проверка на битые ссылки через Screaming Frog.",
    "🎯 Сео-дружественные URL без индексов и дат.",
    "📊 Когортный анализ: как ведут себя пользователи со временем.",
    "🎨 Тёмная тема — теперь стандарт для многих сайтов.",
    "📱 Тильда: подключай свой домен, а не тильдовский поддомен.",
    "🧩 Сброс стилей (reset.css или normalize.css).",
    "⚡ Приоритизируй видимый контент (above the fold).",
    "🎯 Кликабельные карточки товаров, а не только кнопка.",
    "📊 Метрика: цель на подписку, заявку, покупку.",
    "🎨 Псевдоклассы :focus для навигации с клавиатуры.",
    "📱 Жесты для мобильных: свайп, пинч, долгое нажатие.",
    "🧩 Стилизация placeholder в формах.",
    "⚡ CDN для статики — ускоряет загрузку.",
    "🎯 Кнопка 'Заказать звонок' для сайтов услуг.",
    "📊 Юнит-экономика: сколько стоит привлечь пользователя.",
    "🎨 Тильда: добавляй favicon через код в настройках.",
    "📱 Избегай горизонтального скролла на всех разрешениях.",
    "🧩 Прогрессивное улучшение: базовый функционал без JS.",
    "⚡ Кэширование статики в браузере.",
    "🎯 Промо-баннер в шапке — не перекрывай основной контент.",
    "📊 Retention: как часто возвращаются пользователи.",
    "🎨 Дроп-кап (первая буква) для длинных статей.",
    "📱 Тильда: анимация текста при скролле — не злоупотребляй.",
    "🧩 Подвал сайта — тоже навигация: контакты, соцсети, карта сайта.",
    "⚡ Инструменты: PageSpeed Insights, Lighthouse.",
    "🎯 Цветовая слепота — проверяй контраст через симуляторы.",
    "📊 Lifetime Value (LTV) — сколько приносит один клиент.",
    "🎨 Макеты для мобильных, планшетов, десктопов — три размера.",
    "📱 Тильда: используй 'Свой код' для кастомных скриптов.",
    "🧩 Стилизация скроллбара — приятный бонус.",
    "⚡ Минификация CSS/JS через сборщики.",
    "🎯 Чёткий призыв 'в лоб' на баннерах.",
    "📊 Динамика метрик по дням/неделям.",
    "🎨 Тильда: Zero Block позволяет сделать полностью уникальный дизайн.",
    "📱 Новые тренды 2025: моноширинные шрифты для акцентов.",
    "🧩 Не перегружай футер информацией.",
    "⚡ Используй формат .ico для фавикона.",
    "🎯 Понятная навигация: максимум 2-3 уровня меню.",
    "📊 Когортный анализ покажет, когда пользователи отваливаются.",
    "🎨 Эффект печатной машинки для заголовков — работает на тильде.",
    "📱 Тильда: видео на всю ширину экрана.",
    "🧩 Сетка bootstrap или tailwind — выбери свою.",
    "⚡ Шрифты с переменными (variable fonts) — весят меньше.",
    "🎯 Сквозная аналитика от рекламы до покупки.",
    "📊 Тепловые карты внимания — Hotjar, CrazyEgg.",
    "🎨 Не бойся белого пространства.",
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

def get_local_image():
    try:
        images_dir = "images"
        if not os.path.exists(images_dir):
            return None
        images = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        if images:
            selected = random.choice(images)
            return f"/{images_dir}/{selected}"
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
    return ' '.join(keywords) if keywords else 'trading'

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
        requests.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        })
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
    return (f"📰 <b>{title}</b>\n\n{summary}\n\n🔗 <a href='{url}'>Читать</a>\n---\n💡 Alpha Trades")

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

# ========== НОВОСТИ ДИЗАЙНА (свой RSS парсер) ==========

def parse_rss(url):
    """Свой парсер RSS без feedparser"""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        # Пространства имён RSS
        ns = {'': 'http://www.w3.org/2005/Atom'}
        if '{http://www.w3.org/2005/Atom}' in root.tag:
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            items = root.findall('.//atom:entry', ns)
        else:
            items = root.findall('.//item')
        
        news = []
        for item in items[:2]:  # Берём 2 последние новости
            title_elem = item.find('title')
            link_elem = item.find('link')
            if title_elem is not None and link_elem is not None:
                title = title_elem.text
                link = link_elem.text
                # Если заголовок на английском — переводим
                if any(ord(c) < 128 for c in title) and len(title) > 10:
                    try:
                        title = translator.translate(title)
                    except:
                        pass
                news.append({"title": title, "link": link})
        return news
    except Exception as e:
        print(f"Ошибка парсинга RSS {url}: {e}")
        return []

def fetch_design_news():
    """Собирает новости из RSS для дизайна"""
    all_news = []
    for feed_url in DESIGN_RSS_FEEDS:
        news = parse_rss(feed_url)
        all_news.extend(news)
    # Убираем дубликаты по ссылкам
    unique = []
    seen = set()
    for item in all_news:
        if item['link'] not in seen:
            unique.append(item)
            seen.add(item['link'])
    return unique[:5]

def cmd_design_news(chat_id):
    """Отправляет новости дизайна"""
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

# ========== КОМАНДЫ ТРЕЙДИНГА ==========

def cmd_trade_post(chat_id):
    posts = load_trade_posts()
    current_index = load_trade_state()
    if current_index >= len(posts):
        send_message(chat_id, "🏁 Все посты трейдинга опубликованы!")
        return
    post_text = posts[current_index]
    post_text += TRADE_SIGNATURE
    keywords = extract_keywords(post_text)
    image_url = get_image_from_pexels(keywords)
    if not image_url:
        local_img = get_local_image()
        if local_img:
            base_url = "https://webdesign-unified-bot.onrender.com"
            image_url = f"{base_url}{local_img}"
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

# ========== КОМАНДЫ ДИЗАЙНА ==========

def cmd_design_post(chat_id):
    current_index = load_design_state()
    if current_index >= len(DESIGN_TIPS):
        send_message(chat_id, "🏁 Все советы дизайна опубликованы!")
        return
    post_text = DESIGN_TIPS[current_index]
    post_text += DESIGN_SIGNATURE
    keywords_map = {
        'шрифт': 'typography',
        'цвет': 'color palette',
        'мобильн': 'mobile app design',
        'figma': 'figma design',
        'кнопка': 'button ui',
        'сетка': 'grid layout'
    }
    kw = 'web design'
    for ru_kw, en_kw in keywords_map.items():
        if ru_kw in post_text.lower():
            kw = en_kw
            break
    image_url = get_image_from_pexels(kw)
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

<b>Трейдинг канал:</b>
/trade_post — следующий пост
/trade_news — новости
/trade_status — прогресс
/trade_reset — сброс

<b>Дизайн канал:</b>
/design_post — совет
/design_news — новости
/design_status — прогресс
/design_reset — сброс

<b>Общее:</b>
/status — оба прогресса
/help — справка
"""
    send_message(chat_id, help_text)

# ========== WEBHOOK ==========

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data or 'message' not in data:
        return "OK", 200
    chat_id = data['message']['chat']['id']
    text = data['message'].get('text', '').lower()
    print(f"📩 Команда: {text}")
    if text == '/trade_post':
        cmd_trade_post(chat_id)
    elif text == '/trade_news':
        cmd_trade_news(chat_id)
    elif text == '/trade_status':
        cmd_trade_status(chat_id)
    elif text == '/trade_reset':
        cmd_trade_reset(chat_id)
    elif text == '/design_post':
        cmd_design_post(chat_id)
    elif text == '/design_news':
        cmd_design_news(chat_id)
    elif text == '/design_status':
        cmd_design_status(chat_id)
    elif text == '/design_reset':
        cmd_design_reset(chat_id)
    elif text == '/status':
        cmd_status(chat_id)
    elif text == '/help':
        cmd_help(chat_id)
    else:
        send_message(chat_id, "❓ Неизвестная команда. Напиши /help")
    return "OK", 200

@app.route('/')
def home():
    return "Бот работает! 2 канала, 2 поста в день каждый", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
