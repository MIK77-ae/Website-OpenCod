"""
config.py — Конфигурация проекта
================================
Вставьте свои ключи ниже.
"""

import os

# =============================================================================
# PROXY API (для генерации постов)
# =============================================================================
PROXY_API_KEY = os.environ.get("PROXY_API_KEY", "sk-Wn6aMngfsrbCRtoN30ILHSfNFLVJR1mp")
PROXY_API_BASE_URL = "https://api.proxyapi.ru"
MODEL_NAME = "gpt-5.4-mini"
MAX_TOKENS = 800
MAX_TOKENS_PARAM = "max_completion_tokens"
TEMPERATURE = 0.9
API_TIMEOUT = 60

# =============================================================================
# VKONTAKTE API (для публикации постов)
# =============================================================================
# Получить токен: https://vk.com/edit.php?act=settings&section=api
# Подробная инструкция в README.md

# Токен доступа ВК (от сообщества)
VK_ACCESS_TOKEN = os.environ.get("VK_ACCESS_TOKEN", "")

# ID сообщества (можно посмотреть в ссылке сообщества)
# Например, для https://vk.com/club123456789 -> ID = 123456789
VK_GROUP_ID = os.environ.get("VK_GROUP_ID", "")

# =============================================================================
# ПУТИ К ФАЙЛАМ
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAVORITES_FILE = os.path.join(BASE_DIR, "favorites.json")
SCHEDULED_FILE = os.path.join(BASE_DIR, "scheduled_posts.json")
