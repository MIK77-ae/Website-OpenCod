"""
api_client.py — Клиент для ProxyAPI
====================================
Простой клиент для отправки запросов к языковым моделям через ProxyAPI.
"""

import requests
from typing import Optional
from config import PROXY_API_KEY, PROXY_API_BASE_URL, MODEL_NAME, MAX_TOKENS, TEMPERATURE, API_TIMEOUT


class ProxyAPIClient:
    """Клиент для работы с ProxyAPI."""
    
    def __init__(self, api_key: str = None):
        """
        Инициализация клиента.
        
        Args:
            api_key: API-ключ ProxyAPI. Если не указан, берётся из config.py
        """
        self.api_key = api_key or PROXY_API_KEY
        self.base_url = PROXY_API_BASE_URL
    
    def generate_chat(self, messages: list, model: str = MODEL_NAME) -> dict:
        """
        Отправляет запрос к чат-модели через ProxyAPI.
        
        Args:
            messages: список сообщений [{role: str, content: str}, ...]
            model: название модели
        
        Returns:
            dict с ответом модели
        
        Raises:
            Exception: при ошибке API
        """
        url = f"{self.base_url}/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "max_completion_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE
        }
        
        try:
            response = requests.post(
                url, 
                headers=headers, 
                json=payload, 
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.Timeout:
            raise Exception("Превышен тайм-аут запроса. Попробуйте ещё раз.")
        except requests.exceptions.ConnectionError:
            raise Exception("Не удалось подключиться к ProxyAPI. Проверьте интернет-соединение.")
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response else {}
            error_msg = error_data.get("error", {}).get("message", str(e))
            raise Exception(f"Ошибка API: {error_msg}")
        except Exception as e:
            raise Exception(f"Неожиданная ошибка: {str(e)}")
    
    def generate_post(self, prompt: str, tone: str, description: str = None, price: str = None) -> str:
        """
        Генерирует пост с помощью языковой модели.
        
        Args:
            prompt: промпт с информацией о товаре
            tone: тон текста (friendly/exciting/professional/calm)
            description: описание товара
            price: цена или выгода
        
        Returns:
            Сгенерированный текст поста
        """
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Сгенерируй пост в тоне: {tone}"}
        ]
        
        if description:
            messages.append({"role": "user", "content": f"Дополнительная информация: {description}"})
        if price:
            messages.append({"role": "user", "content": f"Цена/выгода: {price}"})
        
        result = self.generate_chat(messages)
        return result["choices"][0]["message"]["content"]


def generate_product_post(
    product_name: str,
    description: str,
    price_info: str,
    tone: str,
    api_key: str = None
) -> str:
    """
    Генерирует уникальный пост для товара через ProxyAPI.
    
    Args:
        product_name: название товара
        description: описание товара
        price_info: цена или выгода
        tone: тон поста
        api_key: API-ключ (опционально)
    
    Returns:
        Готовый текст поста
    """
    client = ProxyAPIClient(api_key)
    
    # Формируем детальный промпт с инструкциями для генерации
    system_prompt = f"""Ты — эксперт по созданию продающих постов для товаров в социальных сетях.

ЗАДАЧА: Напиши оригинальный, интересный пост для товара.

ТОВАР: {product_name}
ОПИСАНИЕ: {description}
ЦЕНА/ВЫГОДА: {price_info if price_info else 'не указана'}

ТОН: {tone}

ТРЕБОВАНИЯ:
1. Заголовок — интригующий, 1-2 строки
2. Основной текст — живой, эмоциональный
3. Описание пользы товара — конкретно
4. 4-6 релевантных хэштегов
5. Один CTA в конце

СТИЛЬ:
- Только эмодзи в тему (без переусердствования, 2-5 штук)
- БЕЗ звездочек (*), дефисов (---), лишних разделителей
- Чистый текст без markdown форматирования
- Избегай шаблонных фраз
- Проверь орфографию перед ответом

ФОРМАТ ОТВЕТА (только текст, без разметки):
[заголовок с эмодзи]

[основной текст]

[хэштеги через пробел]

[короткий CTA с эмодзи]"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Напиши пост для этого товара"}
    ]
    
    result = client.generate_chat(messages)
    post_text = result["choices"][0]["message"]["content"]
    
    # Удаляем лишние символы: звездочки, дефисы, тире, решетки в тексте
    import re
    # Удаляем звездочки и дефис-разделители
    post_text = re.sub(r'\*\s?', '', post_text)
    post_text = re.sub(r'\s*[-—]\s*', '\n', post_text)
    # Удаляем лишние пробелы
    post_text = re.sub(r'\n{3,}', '\n\n', post_text)
    
    return post_text.strip()


# Для тестирования
if __name__ == "__main__":
    test_post = generate_product_post(
        product_name="Умная лампочка",
        description="LED-лампа с управлением через телефон, менять цвета и яркость",
        price_info="990 ₽",
        tone="friendly"
    )
    print(test_post)
