"""
config.py — Конфигурация проекта
================================
Вставьте свои ключи ниже.
"""

import os

# =============================================================================
# PROXY API (для генерации постов)
# =============================================================================
# Ключ хранится в переменной окружения для безопасности
# Windows: set PROXY_API_KEY=ваш-ключ
# Linux/Mac: export PROXY_API_KEY=ваш-ключ

PROXY_API_KEY = os.environ.get("PROXY_API_KEY", "")
PROXY_API_BASE_URL = "https://api.proxyapi.ru"
MODEL_NAME = "gpt-5.4-mini"
MAX_TOKENS = 800
MAX_TOKENS_PARAM = "max_completion_tokens"
TEMPERATURE = 0.9
API_TIMEOUT = 60

# =============================================================================
# VKONTAKTE API (для публикации постов)
# =============================================================================
# Токен и ID хранятся в переменных окружения для безопасности
# Windows: set VK_ACCESS_TOKEN=ваш-токен && set VK_GROUP_ID=123456789
# Linux/Mac: export VK_ACCESS_TOKEN=ваш-токен && export VK_GROUP_ID=123456789

# Токен доступа ВК (из переменной окружения)
VK_ACCESS_TOKEN = os.environ.get("VK_ACCESS_TOKEN", "")

# ID сообщества (из переменной окружения)
VK_GROUP_ID = os.environ.get("VK_GROUP_ID", "")

# =============================================================================
# ПУТИ К ФАЙЛАМ
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAVORITES_FILE = os.path.join(BASE_DIR, "favorites.json")
SCHEDULED_FILE = os.path.join(BASE_DIR, "scheduled_posts.json")
