"""
vk_client.py — Клиент для ВКонтакте API
=======================================
Функции для публикации постов в сообщество ВК.
"""

import requests
from datetime import datetime
from typing import Optional
from config import VK_ACCESS_TOKEN, VK_GROUP_ID


class VKClient:
    """Клиент для работы с ВКонтакте API."""
    
    API_URL = "https://api.vk.com/method"
    
    def __init__(self, access_token: str = None, group_id: str = None):
        """
        Инициализация клиента ВК.
        
        Args:
            access_token: токен доступа ВК
            group_id: ID сообщества
        """
        self.access_token = access_token or VK_ACCESS_TOKEN
        self.group_id = group_id or VK_GROUP_ID
    
    def _make_request(self, method: str, params: dict) -> dict:
        """
        Выполняет запрос к ВК API.
        
        Args:
            method: название метода API
            params: параметры запроса
        
        Returns:
            Ответ API в виде словаря
        """
        url = f"{self.API_URL}/{method}"
        params["access_token"] = self.access_token
        params["v"] = "5.131"
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if "error" in data:
            error = data["error"]
            error_msg = error.get("error_msg", "Unknown error")
            raise Exception(f"VK API Error: {error_msg}")
        
        return data.get("response", {})
    
    def is_configured(self) -> bool:
        """Проверяет, настроен ли клиент (есть токен и ID группы)."""
        return bool(self.access_token and self.group_id)
    
    def get_group_info(self) -> Optional[dict]:
        """
        Получает информацию о сообществе.
        
        Returns:
            Информация о группе или None
        """
        if not self.is_configured():
            return None
        
        try:
            groups = self._make_request("groups.getById", {
                "group_ids": self.group_id
            })
            
            if groups:
                return groups[0]
            return None
        
        except Exception as e:
            print(f"Error getting group info: {e}")
            return None
    
    def post_now(self, message: str) -> dict:
        """
        Публикует пост прямо сейчас.
        
        Args:
            message: текст поста
        
        Returns:
            {'success': True, 'post_id': id} или {'success': False, 'error': message}
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "ВК не настроен. Добавьте токен и ID группы в config.py"
            }
        
        try:
            result = self._make_request("wall.post", {
                "owner_id": f"-{self.group_id}",
                "message": message,
                "from_group": 1
            })
            
            post_id = result.get("post_id")
            
            if post_id:
                return {
                    "success": True,
                    "post_id": post_id,
                    "message": "Пост опубликован!"
                }
            else:
                return {
                    "success": False,
                    "error": "Не удалось опубликовать пост"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def schedule_post(self, message: str, timestamp: int) -> dict:
        """
        Публикует отложенный пост.
        
        Args:
            message: текст поста
            timestamp: Unix-время публикации
        
        Returns:
            {'success': True, 'post_id': id} или {'success': False, 'error': message}
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "ВК не настроен. Добавьте токен и ID группы в config.py"
            }
        
        try:
            result = self._make_request("wall.post", {
                "owner_id": f"-{self.group_id}",
                "message": message,
                "publish_date": timestamp,
                "from_group": 1
            })
            
            post_id = result.get("post_id")
            
            if post_id:
                return {
                    "success": True,
                    "post_id": post_id,
                    "message": f"Пост запланирован на {datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M')}"
                }
            else:
                return {
                    "success": False,
                    "error": "Не удалось запланировать пост"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_scheduled(self, post_id: int, owner_id: str = None) -> bool:
        """
        Удаляет отложенный пост.
        
        Args:
            post_id: ID поста
            owner_id: ID владельца поста
        
        Returns:
            True если успешно
        """
        if not self.is_configured():
            return False
        
        try:
            owner = owner_id or f"-{self.group_id}"
            
            self._make_request("wall.delete", {
                "owner_id": owner,
                "post_id": post_id
            })
            
            return True
        
        except Exception as e:
            print(f"Error deleting scheduled post: {e}")
            return False


def publish_to_vk(message: str, schedule_time: str = None) -> dict:
    """
    Публикует пост в ВК.
    
    Args:
        message: текст поста
        schedule_time: время публикации в формате 'YYYY-MM-DDTHH:MM'
                      Если None — публикация сразу
    
    Returns:
        Результат публикации
    """
    client = VKClient()
    
    if not client.is_configured():
        return {
            "success": False,
            "error": "ВК не настроен. Заполните VK_ACCESS_TOKEN и VK_GROUP_ID в config.py"
        }
    
    if schedule_time:
        try:
            dt = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M")
            timestamp = int(dt.timestamp())
            
            if timestamp <= int(datetime.now().timestamp()):
                return {
                    "success": False,
                    "error": "Время публикации должно быть в будущем"
                }
            
            return client.schedule_post(message, timestamp)
        
        except ValueError:
            return {
                "success": False,
                "error": "Неверный формат времени. Используйте: ГГГГ-ММ-ДДТЧЧ:ММ"
            }
    else:
        return client.post_now(message)
