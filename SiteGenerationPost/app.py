"""
Генератор постов для товаров на Flask

Простой генератор маркетинговых постов без использования нейросетей.
Использует шаблоны для создания продающих текстов.
"""

from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)


# ============================================================
# НАСТРОЙКИ ГЕНЕРАТОРА - легко изменить стиль постов
# ============================================================

# Общий тон постов
# Варианты: "energetic" (энергичный), "professional" (профессиональный),
#           "friendly" (дружелюбный), "luxury" (премиум)
POST_TONE = "friendly"

# Длина поста: "short" (короткий), "medium" (средний), "long" (длинный)
POST_LENGTH = "medium"

# Количество эмодзи: 1-3
EMOJI_COUNT = 2

# Стиль заголовков: "question" (вопрос), "statement" (утверждение), "benefit" (выгода)
TITLE_STYLE = "benefit"

# Стиль CTA (призыва к действию): "soft" (мягкий), "strong" (активный), "curious" (интригующий)
CTA_STYLE = "soft"

# Количество хэштегов
HASHTAG_COUNT = 5


# ============================================================
# ШАБЛОНЫ ПО РАЗНЫМ НАСТРОЕНИЯМ
# ============================================================

# Эмодзи для разных настроений постов
EMOJI_SETS = {
    "energetic": ["🔥", "💪", "⚡", "🚀", "✨", "🎯"],
    "professional": ["📊", "💼", "🎓", "✅", "📈", "🔧"],
    "friendly": ["😊", "❤️", "👍", "🎉", "💛", "🙌"],
    "luxury": ["💎", "👑", "🌟", "✨", "🎩", "🔮"]
}

# CTA шаблоны по стилям
CTA_TEMPLATES = {
    "soft": [
        "Хотите узнать больше? Пишите в комментариях! 💬",
        "Интересует? Оставьте сообщение, расскажу подробнее ✨",
        "Хотите попробовать? Напишите мне в личку 💌"
    ],
    "strong": [
        "Заказывайте прямо сейчас! ⏰",
        "Не упустите возможность - переходите по ссылке 👆",
        "Спешите! Количество ограничено 🔥"
    ],
    "curious": [
        "А вы уже пробовали? Делитесь в комментариях 🤔",
        "Интересно узнать ваше мнение! Пишите 💭",
        "Хотите узнать секрет? Читайте дальше... 🔎"
    ]
}

# Хэштеги
HASHTAG_TEMPLATES = [
    "#{product}_продажа", "#{product}_купить", "#товары", "#покупки",
    "#скидка", "#акция", "#новинка", "#рекомендую", "#качество",
    "#выгода", "#特惠", "#лучшее", "#выбор", "#промо"
]


# ============================================================
# ФУНКЦИИ ГЕНЕРАЦИИ ПОСТА
# ============================================================

def generate_title(product_name, price_benefit, tone):
    """Генерирует заголовок поста"""
    if not product_name:
        product_name = "Товар"

    titles = {
        "question": [
            f"А вы уже знаете про {product_name}?",
            f"Ищете {product_name}? У нас есть!",
            f"Хотите {product_name} по выгодной цене?"
        ],
        "statement": [
            f"Представляем {product_name}! 🎉",
            f"Новинка: {product_name} уже в наличии",
            f"Рекомендуем {product_name}!"
        ],
        "benefit": [
            f"{product_name} - ваша выгода {price_benefit}",
            f"Получите {price_benefit} с {product_name}",
            f"Выгода до {price_benefit} с {product_name}"
        ]
    }
    return random.choice(titles[TITLE_STYLE])


def generate_emoji(tone):
    """Генерирует эмодзи для поста"""
    emojis = EMOJI_SETS.get(tone, EMOJI_SETS["friendly"])
    selected = random.sample(emojis, min(EMOJI_COUNT, len(emojis)))
    return "".join(selected)


def generate_main_text(product_description):
    """Генерирует основной текст поста"""
    if not product_description:
        return ""

    templates = {
        "short": [
            f"Отличное решение для вас: {product_description}",
            f"Идеальный выбор: {product_description}",
            f"То, что нужно: {product_description}"
        ],
        "medium": [
            f"Хотим рассказать вам о {product_description}. Это то, что сделает вашу жизнь лучше!",
            f"Представляем вашему вниманию: {product_description}. Проверенное качество!",
            f"Откройте для себя {product_description}. Отличный выбор для каждого!"
        ],
        "long": [
            f"Мы рады представить вам {product_description}. Этот товар поможет вам решить множество задач и значительно упростит вашу жизнь. Качество проверено временем, а цена приятно удивит!",
            f"Познакомьтесь с {product_description}. Мы тщательно отобрали этот товар для вас, учитывая все ваши потребности. Отличное соотношение цены и качества, долгий срок службы и полная гарантия!",
            f"У нас для вас отличная новость! Появился {product_description}. Это именно то, что вы искали - сочетание функциональности, качества и разумной цены. Заказывайте прямо сейчас!"
        ]
    }
    return random.choice(templates[POST_LENGTH])


def generate_benefit(price_benefit):
    """Генерирует описание выгоды для покупателя"""
    if not price_benefit:
        price_benefit = "отличная цена"

    benefit_templates = [
        f"Вы получаете {price_benefit} - это отличная возможность сэкономить!",
        f"Цена {price_benefit} - такое предложение нельзя упустить!",
        f"Ваша выгода: {price_benefit}. Спешите сделать заказ!",
        f"Только сейчас: {price_benefit}. Не упустите шанс!"
    ]
    return random.choice(benefit_templates)


def generate_hashtags(product_name):
    """Генерирует хэштеги для поста"""
    product_clean = product_name.replace(" ", "_") if product_name else "товар"

    available_tags = [tag.format(product=product_clean) for tag in HASHTAG_TEMPLATES]
    selected_tags = random.sample(available_tags, min(HASHTAG_COUNT, len(available_tags)))
    return " ".join(selected_tags)


def generate_cta():
    """Генерирует CTA (призыв к действию)"""
    ctas = CTA_TEMPLATES.get(CTA_STYLE, CTA_TEMPLATES["soft"])
    return random.choice(ctas)


def generate_post(product_name, product_description, price_benefit, tone):
    """Генерирует готовый пост"""
    # Собираем все части поста
    title = generate_title(product_name, price_benefit, tone)
    emoji = generate_emoji(tone)
    main_text = generate_main_text(product_description)
    benefit = generate_benefit(price_benefit)
    hashtags = generate_hashtags(product_name)
    cta = generate_cta()

    # Формируем итоговый пост
    post_parts = [
        f"{title} {emoji}",
        "",
        main_text,
        "",
        benefit,
        "",
        cta,
        "",
        hashtags
    ]

    return "\n".join(post_parts)


# ============================================================
# МАРШРУТЫ ПРИЛОЖЕНИЯ
# ============================================================

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """Обработка генерации поста"""
    data = request.get_json()

    # Получаем данные из формы
    product_name = data.get('product_name', '').strip()
    product_description = data.get('product_description', '').strip()
    price_benefit = data.get('price_benefit', '').strip()
    tone = data.get('tone', 'friendly')

    # Валидация - описание товара обязательно
    if not product_description:
        return jsonify({
            'success': False,
            'error': 'Добавьте описание товара'
        })

    # Генерируем пост
    post = generate_post(product_name, product_description, price_benefit, tone)

    return jsonify({
        'success': True,
        'post': post
    })


if __name__ == '__main__':
    # Запуск приложения
    # host='0.0.0.0' - доступ с других устройств в сети
    # port=5000 - порт по умолчанию для Flask
    # debug=True - режим отладки (только для разработки!)
    app.run(host='127.0.0.1', port=5001, debug=True)