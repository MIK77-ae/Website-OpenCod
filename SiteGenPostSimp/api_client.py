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

ТРЕБОВАНИЯ К ПОСТУ:
1. Заголовок — интригующий, привлекающий внимание (1-2 строки)
2. Основной текст — живой, эмоциональный, с историей или историей успеха
3. Описание пользы товара для покупателя — конкретно и убедительно
4. 4-6 релевантных хэштегов
5. CTA (призыв к действию) — один в конце

СТИЛЬ:
- Тон: {tone}
- Оригинальность: избегай шаблонных фраз типа "идеальный выбор" или "незаменимая вещь"
- Эмоции: используй разные эмоции ({tone})
- Формат: используй эмодзи, но не переусердствуй

ФОРМАТ ОТВЕТА:
[ЗАГОЛОВОК]

[основной текст]

[хэштеги]

[CTA]"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Напиши пост для этого товара"}
    ]
    
    result = client.generate_chat(messages)
    return result["choices"][0]["message"]["content"]


# Для тестирования
if __name__ == "__main__":
    test_post = generate_product_post(
        product_name="Умная лампочка",
        description="LED-лампа с управлением через телефон, менять цвета и яркость",
        price_info="990 ₽",
        tone="friendly"
    )
    print(test_post)
