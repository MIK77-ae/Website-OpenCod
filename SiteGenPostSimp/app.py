"""
SiteGenPostSimp - Генератор постов для товаров
==============================================
Flask-сайт для создания продающих постов с помощью ИИ (ProxyAPI).
Без базы данных, простой код для понимания.
"""

from flask import Flask, render_template, request, jsonify
from api_client import generate_product_post

app = Flask(__name__)


# =============================================================================
# НАСТРОЙКИ ТОНОВ ПОСТОВ
# =============================================================================
# Каждый тон влияет на стиль генерации текста языковой моделью
#-------------------------------------------------------------------------------
# friendly    — дружелюбный, тёплый, располагающий, с улыбкой
# exciting    — восторженный, энергичный, с энтузиазмом
# professional — деловой, уверенный, с акцентом на результат
# calm        — спокойный, размеренный, расслабляющий
#-------------------------------------------------------------------------------

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
# МАРШРУТЫ FLASK
# =============================================================================

@app.route('/')
def index():
    """
    Главная страница с формой генератора постов.
    
    Returns:
        Отрендеренный шаблон index.html
    """
    return render_template('index.html', moods=POST_MOODS)


@app.route('/generate', methods=['POST'])
def generate():
    """
    Обработчик формы генерации поста.
    
    Получает данные из формы, отправляет запрос к ProxyAPI,
    возвращает JSON с результатом.
    
    Returns:
        JSON: {'success': True, 'post': text} или {'success': False, 'error': message}
    """
    # Получаем данные из формы
    product = request.form.get('product', '')
    description = request.form.get('description', '')
    price_info = request.form.get('price_info', '')
    tone = request.form.get('mood', 'friendly')
    
    # Проверяем обязательное поле описания
    if not description or not description.strip():
        return jsonify({
            'success': False, 
            'error': 'Добавьте описание товара'
        })
    
    # Если название товара не указано, используем значение по умолчанию
    if not product or not product.strip():
        product = "Этот товар"
    
    try:
        # Отправляем запрос к ProxyAPI
        post = generate_product_post(
            product_name=product.strip(),
            description=description.strip(),
            price_info=price_info.strip() if price_info else '',
            tone=tone
        )
        
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
# ЗАПУСК ПРИЛОЖЕНИЯ
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Generator Postov")
    print("=" * 60)
    print("Open in browser: http://127.0.0.1:5004")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5004)
