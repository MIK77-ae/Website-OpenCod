"""
SiteGenPostSimp - Генератор постов для товаров
==============================================
Flask-сайт для создания продающих постов с помощью ИИ (ProxyAPI).
Публикация в ВК, избранное, отложенные посты.
"""

from flask import Flask, render_template, request, jsonify, session
from api_client import generate_product_post
from vk_client import publish_to_vk
from favorites import add_to_favorites, get_favorites, delete_favorite
from scheduled import add_scheduled, get_scheduled, delete_scheduled

app = Flask(__name__)
app.secret_key = "post-generator-secret-key-2024"


# =============================================================================
# НАСТРОЙКИ ТОНОВ ПОСТОВ
# =============================================================================

POST_MOODS = {
    'friendly': {
        'description': 'Дружелюбный',
        'emoji': '😊',
        'keywords': 'тёплый, дружеский, располагающий, с юмором'
    },
    'exciting': {
        'description': 'Восторженный',
        'emoji': '🔥',
        'keywords': 'эмоциональный, энергичный, яркий, вдохновляющий'
    },
    'professional': {
        'description': 'Деловой',
        'emoji': '📊',
        'keywords': 'деловой, уверенный, профессиональный, убедительный'
    },
    'calm': {
        'description': 'Спокойный',
        'emoji': '🌿',
        'keywords': 'спокойный, размеренный, мягкий, умиротворяющий'
    }
}


# =============================================================================
# ГЛАВНАЯ СТРАНИЦА
# =============================================================================

@app.route('/')
def index():
    """Главная страница с формой генератора постов."""
    return render_template('index.html', moods=POST_MOODS)


# =============================================================================
# ГЕНЕРАЦИЯ ПОСТА
# =============================================================================

@app.route('/generate', methods=['POST'])
def generate():
    """Генерирует пост с помощью ИИ."""
    product = request.form.get('product', '')
    description = request.form.get('description', '')
    price_info = request.form.get('price_info', '')
    tone = request.form.get('mood', 'friendly')
    
    if not description or not description.strip():
        return jsonify({
            'success': False, 
            'error': 'Добавьте описание товара'
        })
    
    if not product or not product.strip():
        product = "Этот товар"
    
    try:
        post = generate_product_post(
            product_name=product.strip(),
            description=description.strip(),
            price_info=price_info.strip() if price_info else '',
            tone=tone
        )
        
        session['current_post'] = post
        session['current_product'] = product.strip()
        session['current_tone'] = tone
        
        return jsonify({
            'success': True, 
            'post': post
        })
    
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        })


# =============================================================================
# ИЗБРАННОЕ
# =============================================================================

@app.route('/favorites/add', methods=['POST'])
def add_favorite():
    """Добавляет пост в избранное."""
    data = request.get_json()
    post_text = data.get('post_text', '')
    product = data.get('product', '')
    tone = data.get('tone', '')
    
    if not post_text:
        return jsonify({'success': False, 'error': 'Пустой пост'})
    
    post = add_to_favorites(post_text, product, tone)
    
    return jsonify({
        'success': True,
        'message': 'Пост добавлен в избранное',
        'post': post
    })


@app.route('/favorites', methods=['GET'])
def list_favorites():
    """Получает список избранных постов."""
    favorites = get_favorites()
    
    return jsonify({
        'success': True,
        'favorites': favorites
    })


@app.route('/favorites/<int:post_id>', methods=['GET'])
def get_favorite(post_id):
    """Получает пост из избранного по ID."""
    post = get_favorites()
    for p in post:
        if p["id"] == post_id:
            return jsonify(p)
    return jsonify({'success': False, 'error': 'Пост не найден'}), 404


@app.route('/favorites/<int:post_id>', methods=['DELETE'])
def remove_favorite(post_id):
    """Удаляет пост из избранного."""
    success = delete_favorite(post_id)
    
    return jsonify({
        'success': success,
        'message': 'Пост удалён из избранного' if success else 'Пост не найден'
    })


@app.route('/post/update', methods=['POST'])
def update_post():
    """Обновляет текст поста (после редактирования)."""
    data = request.get_json()
    post_text = data.get('post_text', '')
    
    if not post_text:
        return jsonify({'success': False, 'error': 'Пустой пост'})
    
    # Обновляем пост в сессии
    session['current_post'] = post_text
    
    return jsonify({
        'success': True,
        'post': post_text
    })


# =============================================================================
# ПУБЛИКАЦИЯ В ВК
# =============================================================================

@app.route('/vk/publish', methods=['POST'])
def vk_publish():
    """Публикует пост в ВК сейчас."""
    data = request.get_json()
    post_text = data.get('post_text', '')
    
    if not post_text:
        return jsonify({'success': False, 'error': 'Пустой пост'})
    
    result = publish_to_vk(post_text)
    
    return jsonify(result)


@app.route('/vk/schedule', methods=['POST'])
def vk_schedule():
    """Планирует пост - сохраняет в отложенные."""
    data = request.get_json()
    post_text = data.get('post_text', '')
    schedule_time = data.get('schedule_time', '')
    
    if not post_text:
        return jsonify({'success': False, 'error': 'Пустой пост'})
    
    if not schedule_time:
        return jsonify({'success': False, 'error': 'Укажите время публикации'})
    
    # Всегда сохраняем пост в локальный список отложенных
    from scheduled import add_scheduled
    
    product_name = session.get('current_product', '')
    tone = session.get('current_tone', '')
    
    # Пробуем отправить в ВК если настроен
    result = publish_to_vk(post_text, schedule_time)
    vk_post_id = result.get('post_id') if result.get('success') else None
    
    # Сохраняем в локальный список ВСЕГДА
    saved_post = add_scheduled(
        post_text=post_text,
        schedule_time=schedule_time,
        product_name=product_name,
        tone=tone,
        vk_post_id=vk_post_id
    )
    
    # Формируем сообщение
    if result.get('success'):
        message = f"Пост запланирован на {schedule_time}"
    else:
        message = f"Пост сохранён локально. ВК: {result.get('error', 'не настроен')}"
    
    return jsonify({
        'success': True,
        'post_id': saved_post['id'],
        'message': message
    })


@app.route('/vk/status', methods=['GET'])
def vk_status():
    """Проверяет статус подключения к ВК."""
    from vk_client import VKClient
    
    client = VKClient()
    
    if not client.is_configured():
        return jsonify({
            'configured': False,
            'message': 'ВК не настроен. Добавьте токен и ID группы в config.py'
        })
    
    group_info = client.get_group_info()
    
    if group_info:
        return jsonify({
            'configured': True,
            'group_name': group_info.get('name', 'Unknown'),
            'group_id': client.group_id
        })
    
    return jsonify({
        'configured': False,
        'message': 'Не удалось получить информацию о группе'
    })


# =============================================================================
# ОТЛОЖЕННЫЕ ПОСТЫ
# =============================================================================

@app.route('/scheduled', methods=['GET'])
def list_scheduled():
    """Получает список запланированных постов."""
    scheduled = get_scheduled()
    
    return jsonify({
        'success': True,
        'scheduled': scheduled
    })


@app.route('/scheduled/<int:post_id>', methods=['DELETE'])
def remove_scheduled(post_id):
    """Удаляет запланированный пост."""
    from vk_client import VKClient
    
    post = None
    for p in get_scheduled():
        if p['id'] == post_id:
            post = p
            break
    
    if post and post.get('vk_post_id'):
        client = VKClient()
        client.delete_scheduled(post['vk_post_id'], f"-{client.group_id}")
    
    success = delete_scheduled(post_id)
    
    return jsonify({
        'success': success,
        'message': 'Пост удалён' if success else 'Пост не найден'
    })


# =============================================================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("GENERATOR POSTOV")
    print("=" * 60)
    print("Open in browser: http://127.0.0.1:5004")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5004)
