"""
Генератор постов для товаров на Flask с ProxyAPI
"""

from flask import Flask, render_template, request, jsonify
import requests
import re

app = Flask(__name__)

# ============================================================
# НАСТРОЙКИ PROXYAPI
# ============================================================

PROXY_API_KEY = "sk-Wn6aMngfsrbCRtoN30ILHSfNFLVJR1mp"
PROXY_API_URL = "https://api.proxyapi.ru/openai/v1/chat/completions"
MODEL = "gpt-5.4-mini"

# ============================================================
# НАСТРОЙКИ ГЕНЕРАТОРА
# ============================================================

TONES = {
    "friendly": "Дружелюбный, тёплый, располагающий",
    "energetic": "Энергичный, динамичный, мотивирующий",
    "professional": "Профессиональный, деловой, убедительный",
    "luxury": "Премиум, элегантный, эксклюзивный",
    "humor_soft": "С мягким юмором, лёгкий, весёлый",
    "humor_irony": "С иронией, с подтекстом, умный",
    "humor_crazy": "Экстремальный юмор, яркий, эмоциональный",
    "curious": "Интригующий, загадочный, вызывающий интерес",
    "inspirational": "Вдохновляющий, мотивирующий, позитивный",
    "romantic": "Романтичный, нежный, чувственный",
    "urgent": "Срочный, спешный, побуждающий",
    "trust": "Доверительный, надёжный, проверенный",
    "expert": "Экспертный, авторитетный, профессиональный",
    "fun": "Развлекательный, игривый, расслабленный",
    "minimal": "Краткий, лаконичный, без лишних слов"
}


def parse_product_url(url):
    """Быстрый парсинг товара со страницы"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
        }
        
        response = requests.get(url, headers=headers, timeout=8)
        
        if response.status_code != 200:
            return None, f"Ошибка {response.status_code}"
        
        text = response.text
        
        # Определяем сайт
        is_yandex = 'yandex.ru' in url.lower()
        is_ozon = 'ozon.ru' in url.lower()
        is_wb = 'wildberries.ru' in url.lower()
        
        title = None
        price = None
        
        # Яндекс
        if is_yandex:
            # Ищем title
            match = re.search(r'<title>([^<]+)</title>', text, re.I)
            if match:
                title = match.group(1).split('|')[0].split('-')[0].strip()
            # Ищем цену
            match = re.search(r'(\d+[\d\s]*)\s*₽', text)
            if match:
                price = match.group(1).strip()
        
        # Ozon
        elif is_ozon:
            match = re.search(r'<title>([^<]+)</title>', text, re.I)
            if match:
                title = match.group(1).split('|')[0].strip()
            match = re.search(r'(\d+[\d\s]*)\s*₽', text)
            if match:
                price = match.group(1).strip()
        
        # Wildberries
        elif is_wb:
            match = re.search(r'<title>([^<]+)</title>', text, re.I)
            if match:
                title = match.group(1).split('|')[0].strip()
            match = re.search(r'(\d+[\d\s]*)\s*₽', text)
            if match:
                price = match.group(1).strip()
        
        # Общее
        if not title:
            match = re.search(r'<title>([^<]+)</title>', text, re.I)
            if match:
                title = match.group(1).split('|')[0].split('-')[0].strip()
        
        if title or price:
            return {'title': title, 'price': price, 'url': url}, None
        
        return None, "Данные не найдены"
    
    except requests.exceptions.Timeout:
        return None, "Тайм-аут"
    except Exception as e:
        return None, str(e)[:30]


def generate_post_with_ai(product_url, product_description, tone):
    """Генерирует пост с помощью языковой модели ProxyAPI"""
    tone_description = TONES.get(tone, TONES["friendly"])
    
    # Пробуем прочитать ссылку
    product_info = ""
    link_read = False
    
    if product_url and not product_url.startswith('http'):
        product_url = 'https://' + product_url
    
    if product_url:
        info, error = parse_product_url(product_url)
        
        if info and info.get('title'):
            link_read = True
            product_info += f"Название: {info['title']}\n"
            if info.get('price'):
                product_info += f"Цена: {info['price']} ₽\n"
        elif product_url:
            product_info += f"Ссылка: {product_url}\n"
    
    # Добавляем описание
    if product_description:
        if product_info:
            product_info += f"Описание: {product_description}\n"
        else:
            product_info = f"Описание: {product_description}\n"
    
    if not product_info:
        product_info = "Товар без описания"
    
    prompt = f"""Ты - профессиональный копирайтер. Создай маркетинговый пост о товаре.

Информация о товаре:
{product_info}

Стиль поста: {tone_description}

Требования:
1. Оригинальный текст - НЕ шаблонный
2. Заголовок с эмодзи
3. Описание товара и его преимущества
4. 4-6 хэштегов
5. CTA - призыв к действию

Если товар с маркетплейса - учти: быстрая доставка, гарантия, возврат.

Пост на русском языке, 100-200 слов."""

    headers = {
        "Authorization": f"Bearer {PROXY_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
        "max_completion_tokens": 1500
    }

    try:
        response = requests.post(PROXY_API_URL, headers=headers, json=data, timeout=60)

        if response.status_code == 200:
            result = response.json()
            post = result["choices"][0]["message"]["content"]
            return post, link_read, None
        else:
            error_msg = f"Ошибка API: {response.status_code}"
            return None, False, error_msg
    except requests.exceptions.Timeout:
        return None, False, "Время ожидания истекло"
    except Exception as e:
        return None, False, f"Ошибка: {str(e)}"


@app.route('/')
def index():
    return render_template('index.html', tones=TONES)


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()

    product_url = data.get('product_url', '').strip()
    product_description = data.get('product_description', '').strip()
    tone = data.get('tone', 'friendly')

    if not product_url and not product_description:
        return jsonify({
            'success': False,
            'error': 'Добавьте ссылку или описание товара'
        })

    post, link_read, error = generate_post_with_ai(product_url, product_description, tone)

    if error:
        return jsonify({'success': False, 'error': error})

    return jsonify({'success': True, 'post': post, 'link_read': link_read})


if __name__ == '__main__':
    app.run(host='192.168.1.14', port=5003, debug=False)