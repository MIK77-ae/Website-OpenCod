"""
Генератор постов для товаров на Flask с ProxyAPI

Использует языковую модель для генерации оригинальных постов по ссылке или описанию.
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
    "friendly": "Дружелюбный, теплый, располагающий",
    "energetic": "Энергичный, динамичный, мотивирующий",
    "professional": "Профессиональный, деловой, убедительный",
    "luxury": "Премиум, элегантный, эксклюзивный",
    "humor": "С юмором, веселый, легкий",
    "curious": "Интригующий, загадочный, вызывающий интерес",
    "inspirational": "Вдохновляющий, мотивирующий, позитивный"
}


def get_product_info_from_url(url):
    """Пытается получить информацию о товаре со страницы"""
    try:
        clean_url = url.split('?')[0] if '?' in url else url
        
        # Более полная эмуляция браузера
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(clean_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            text = response.text
            
            # Ищем название товара
            title_match = re.search(r'<title>([^<]+)</title>', text, re.I)
            if title_match:
                title = title_match.group(1).split('|')[0].split('-')[0].strip()
            else:
                # Пробуем найти в JSON
                title_match = re.search(r'"name"\s*:\s*"([^"]+)"', text)
                title = title_match.group(1) if title_match else None
            
            # Ищем цену - несколько паттернов
            price = None
            for pattern in [r'"price"\s*:\s*(\d+)', r'(\d+[\d\s]*)\s*₽', r'data-price="(\d+)"']:
                match = re.search(pattern, text)
                if match:
                    price = match.group(1).strip()
                    break
            
            # Ищем рейтинг
            rating_match = re.search(r'"rating"\s*:\s*(\d+\.?\d*)', text)
            rating = rating_match.group(1) if rating_match else None
            
            return {
                'title': title,
                'price': price,
                'rating': rating,
                'url': clean_url
            }
        elif response.status_code == 403:
            return {'error': 'Доступ запрещён - защита сайта'}
        elif response.status_code == 404:
            return {'error': 'Товар не найден'}
        else:
            return {'error': f'Ошибка: {response.status_code}'}
    
    except requests.exceptions.Timeout:
        return {'error': 'Время ожидания истекло'}
    except Exception as e:
        return {'error': f'Ошибка: {str(e)}'}


def generate_post_with_ai(product_info, tone):
    """Генерирует пост с помощью языковой модели ProxyAPI"""
    tone_description = TONES.get(tone, TONES["friendly"])
    
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
            return post, None
        else:
            error_msg = f"Ошибка API: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('error', {}).get('message', '')}"
            except:
                pass
            return None, error_msg
    except requests.exceptions.Timeout:
        return None, "Время ожидания истекло"
    except Exception as e:
        return None, f"Ошибка: {str(e)}"


@app.route('/')
def index():
    return render_template('index.html', tones=TONES)


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()

    product_url = data.get('product_url', '').strip()
    product_description = data.get('product_description', '').strip()
    tone = data.get('tone', 'friendly')

    # Обязательно ссылка
    if not product_url:
        return jsonify({
            'success': False,
            'error': 'Добавьте ссылку на товар'
        })

    # Добавляем https если нужно
    if not product_url.startswith(('http://', 'https://')):
        product_url = 'https://' + product_url

    # Пробуем получить данные со страницы
    info = get_product_info_from_url(product_url)
    
    # Если не получилось и есть описание - используем его
    if info and 'error' in info:
        if not product_description:
            return jsonify({
                'success': False,
                'error': 'Не удалось прочитать ссылку. Добавьте описание товара вручную.'
            })
        # Используем описание вместо ссылки
        product_info = f"Ссылка: {product_url.split('?')[0]}\nОписание: {product_description}\n"
    elif info:
        # Успешно получили данные
        product_info = ""
        if info.get('title'):
            product_info += f"Название: {info['title']}\n"
        if info.get('price'):
            product_info += f"Цена: {info['price']} ₽\n"
        if info.get('rating'):
            product_info += f"Рейтинг: {info['rating']}/5\n"
        # Дополняем описанием если есть
        if product_description:
            product_info += f"Доп. описание: {product_description}\n"
    else:
        # Нет данных - используем описание или URL
        if product_description:
            product_info = f"Описание: {product_description}\n"
        else:
            product_info = f"Ссылка на товар: {product_url}\n"

    # Генерируем пост
    post, error = generate_post_with_ai(product_info, tone)

    if error:
        return jsonify({'success': False, 'error': error})

    return jsonify({'success': True, 'post': post})


if __name__ == '__main__':
    app.run(host='192.168.1.14', port=5002, debug=False)