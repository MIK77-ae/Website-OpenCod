"""
scheduled.py — Отложенные посты
==============================
Управление запланированными постами (сохранение в JSON файл).
"""

import json
import os
from datetime import datetime
from typing import List, Optional
from config import SCHEDULED_FILE


class ScheduledManager:
    """Менеджер отложенных постов."""
    
    def __init__(self, storage_file: str = None):
        """
        Инициализация менеджера.
        
        Args:
            storage_file: путь к файлу хранения
        """
        self.storage_file = storage_file or SCHEDULED_FILE
        self._ensure_file()
    
    def _ensure_file(self):
        """Создаёт файл если его нет."""
        if not os.path.exists(self.storage_file):
            self._save([])
    
    def _load(self) -> List[dict]:
        """Загружает список отложенных постов."""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save(self, data: List[dict]):
        """Сохраняет список отложенных постов."""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add(self, post_text: str, schedule_time: str, product_name: str = "", 
            tone: str = "", vk_post_id: int = None) -> dict:
        """
        Добавляет запланированный пост.
        
        Args:
            post_text: текст поста
            schedule_time: время публикации (формат: YYYY-MM-DDTHH:MM)
            product_name: название товара
            tone: тон поста
            vk_post_id: ID поста в ВК (если уже опубликован)
        
        Returns:
            Запланированный пост с ID
        """
        scheduled = self._load()
        
        try:
            dt = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M")
            timestamp = int(dt.timestamp())
        except ValueError:
            raise ValueError("Неверный формат времени. Используйте: ГГГГ-ММ-ДДТЧЧ:ММ")
        
        new_post = {
            "id": int(datetime.now().timestamp()),
            "text": post_text,
            "product": product_name,
            "tone": tone,
            "schedule_time": schedule_time,
            "timestamp": timestamp,
            "vk_post_id": vk_post_id,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "scheduled"
        }
        
        scheduled.append(new_post)
        self._save(scheduled)
        
        return new_post
    
    def get_all(self) -> List[dict]:
        """Получает все запланированные посты."""
        return self._load()
    
    def get_upcoming(self) -> List[dict]:
        """Получает будущие запланированные посты."""
        scheduled = self._load()
        now = int(datetime.now().timestamp())
        
        return [p for p in scheduled if p["timestamp"] > now and p["status"] == "scheduled"]
    
    def get(self, post_id: int) -> Optional[dict]:
        """Получает пост по ID."""
        scheduled = self._load()
        
        for post in scheduled:
            if post["id"] == post_id:
                return post
        
        return None
    
    def update_status(self, post_id: int, status: str, vk_post_id: int = None) -> bool:
        """
        Обновляет статус поста.
        
        Args:
            post_id: ID поста
            status: новый статус ('published', 'failed')
            vk_post_id: ID поста в ВК
        """
        scheduled = self._load()
        
        for post in scheduled:
            if post["id"] == post_id:
                post["status"] = status
                if vk_post_id:
                    post["vk_post_id"] = vk_post_id
                self._save(scheduled)
                return True
        
        return False
    
    def delete(self, post_id: int) -> bool:
        """Удаляет запланированный пост."""
        scheduled = self._load()
        original_count = len(scheduled)
        
        scheduled = [p for p in scheduled if p["id"] != post_id]
        
        if len(scheduled) < original_count:
            self._save(scheduled)
            return True
        
        return False
    
    def clear_published(self) -> int:
        """Удаляет все опубликованные посты."""
        scheduled = self._load()
        original_count = len(scheduled)
        
        scheduled = [p for p in scheduled if p["status"] == "scheduled"]
        
        deleted = original_count - len(scheduled)
        self._save(scheduled)
        
        return deleted


def add_scheduled(post_text: str, schedule_time: str, product_name: str = "", 
                  tone: str = "", vk_post_id: int = None) -> dict:
    """Удобная функция для добавления запланированного поста."""
    manager = ScheduledManager()
    return manager.add(post_text, schedule_time, product_name, tone, vk_post_id)


def get_scheduled() -> List[dict]:
    """Получает все запланированные посты."""
    manager = ScheduledManager()
    return manager.get_all()


def get_upcoming() -> List[dict]:
    """Получает будущие запланированные посты."""
    manager = ScheduledManager()
    return manager.get_upcoming()


def delete_scheduled(post_id: int) -> bool:
    """Удаляет запланированный пост."""
    manager = ScheduledManager()
    return manager.delete(post_id)
