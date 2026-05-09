"""
favorites.py — Избранные посты
==============================
Управление избранными постами (сохранение в JSON файл).
"""

import json
import os
from datetime import datetime
from typing import List, Optional
from config import FAVORITES_FILE


class FavoritesManager:
    """Менеджер избранных постов."""
    
    def __init__(self, storage_file: str = None):
        """
        Инициализация менеджера.
        
        Args:
            storage_file: путь к файлу хранения
        """
        self.storage_file = storage_file or FAVORITES_FILE
        self._ensure_file()
    
    def _ensure_file(self):
        """Создаёт файл если его нет."""
        if not os.path.exists(self.storage_file):
            self._save([])
    
    def _load(self) -> List[dict]:
        """Загружает список избранного."""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save(self, data: List[dict]):
        """Сохраняет список избранного."""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add(self, post_text: str, product_name: str = "", tone: str = "") -> dict:
        """
        Добавляет пост в избранное.
        
        Args:
            post_text: текст поста
            product_name: название товара
            tone: тон поста
        
        Returns:
            Добавленный пост с ID
        """
        favorites = self._load()
        
        new_post = {
            "id": int(datetime.now().timestamp()),
            "text": post_text,
            "product": product_name,
            "tone": tone,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        favorites.insert(0, new_post)
        self._save(favorites)
        
        return new_post
    
    def get_all(self) -> List[dict]:
        """Получает все избранные посты."""
        return self._load()
    
    def get(self, post_id: int) -> Optional[dict]:
        """
        Получает пост по ID.
        
        Args:
            post_id: ID поста
        
        Returns:
            Пост или None
        """
        favorites = self._load()
        
        for post in favorites:
            if post["id"] == post_id:
                return post
        
        return None
    
    def delete(self, post_id: int) -> bool:
        """
        Удаляет пост из избранного.
        
        Args:
            post_id: ID поста
        
        Returns:
            True если удалён
        """
        favorites = self._load()
        original_count = len(favorites)
        
        favorites = [p for p in favorites if p["id"] != post_id]
        
        if len(favorites) < original_count:
            self._save(favorites)
            return True
        
        return False
    
    def clear(self):
        """Очищает всё избранное."""
        self._save([])


def add_to_favorites(post_text: str, product_name: str = "", tone: str = "") -> dict:
    """
    Удобная функция для добавления в избранное.
    
    Args:
        post_text: текст поста
        product_name: название товара
        tone: тон поста
    
    Returns:
        Добавленный пост
    """
    manager = FavoritesManager()
    return manager.add(post_text, product_name, tone)


def get_favorites() -> List[dict]:
    """Получает все избранные посты."""
    manager = FavoritesManager()
    return manager.get_all()


def delete_favorite(post_id: int) -> bool:
    """Удаляет пост из избранного."""
    manager = FavoritesManager()
    return manager.delete(post_id)
