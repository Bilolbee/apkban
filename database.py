"""
Telegram Anti-APK Security Bot - Strike Database
Foydalanuvchilar qoidabuzarliklarini saqlash va boshqarish
"""

import json
import os
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class StrikeDatabase:
    """
    Strike tizimini boshqarish uchun JSON asosidagi database.
    
    Har bir foydalanuvchi uchun guruh bo'yicha strike saqlanadi.
    Ma'lumotlar strukturasi:
    {
        "chat_id_user_id": {
            "strikes": 3,
            "last_strike": "2024-01-15T10:30:00",
            "username": "user123",
            "first_name": "John"
        }
    }
    """
    
    def __init__(self, db_file: str = 'strikes.json'):
        """
        Database yaratish yoki yuklash.
        
        Args:
            db_file: JSON fayl nomi
        """
        self.db_file = db_file
        self.data: Dict[str, dict] = {}
        self._load()
    
    def _load(self) -> None:
        """Ma'lumotlarni fayldan yuklash"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                logger.info(f"Database yuklandi: {len(self.data)} ta yozuv")
            except json.JSONDecodeError as e:
                logger.error(f"Database yuklashda JSON xatosi: {e}")
                self.data = {}
            except Exception as e:
                logger.error(f"Database yuklashda xato: {e}")
                self.data = {}
        else:
            logger.info("Yangi database yaratildi")
            self.data = {}
    
    def _save(self) -> bool:
        """Ma'lumotlarni faylga saqlash"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Database saqlashda xato: {e}")
            return False
    
    def _get_key(self, chat_id: int, user_id: int) -> str:
        """
        Foydalanuvchi uchun unique key yaratish.
        
        Args:
            chat_id: Guruh ID
            user_id: Foydalanuvchi ID
            
        Returns:
            Unique key string
        """
        return f"{chat_id}_{user_id}"
    
    def add_strike(
        self,
        chat_id: int,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None
    ) -> int:
        """
        Foydalanuvchiga strike qo'shish.
        
        Args:
            chat_id: Guruh ID
            user_id: Foydalanuvchi ID
            username: Foydalanuvchi username (ixtiyoriy)
            first_name: Foydalanuvchi ismi (ixtiyoriy)
            
        Returns:
            Hozirgi strike soni
        """
        key = self._get_key(chat_id, user_id)
        
        if key not in self.data:
            self.data[key] = {
                'strikes': 0,
                'last_strike': None,
                'username': username,
                'first_name': first_name
            }
        
        self.data[key]['strikes'] += 1
        self.data[key]['last_strike'] = datetime.now().isoformat()
        
        if username:
            self.data[key]['username'] = username
        if first_name:
            self.data[key]['first_name'] = first_name
        
        self._save()
        
        logger.info(
            f"Strike qo'shildi: {username or user_id} "
            f"(guruh: {chat_id}, strike: {self.data[key]['strikes']})"
        )
        
        return self.data[key]['strikes']
    
    def get_strikes(self, chat_id: int, user_id: int) -> int:
        """
        Foydalanuvchining hozirgi strike sonini olish.
        
        Args:
            chat_id: Guruh ID
            user_id: Foydalanuvchi ID
            
        Returns:
            Strike soni (0 agar yozuv bo'lmasa)
        """
        key = self._get_key(chat_id, user_id)
        if key in self.data:
            return self.data[key].get('strikes', 0)
        return 0
    
    def reset_strikes(self, chat_id: int, user_id: int) -> bool:
        """
        Foydalanuvchi strike'larini tozalash.
        
        Args:
            chat_id: Guruh ID
            user_id: Foydalanuvchi ID
            
        Returns:
            True agar muvaffaqiyatli, False aks holda
        """
        key = self._get_key(chat_id, user_id)
        if key in self.data:
            del self.data[key]
            self._save()
            logger.info(f"Strike'lar tozalandi: {user_id} (guruh: {chat_id})")
            return True
        return False
    
    def get_user_info(self, chat_id: int, user_id: int) -> Optional[dict]:
        """
        Foydalanuvchi ma'lumotlarini olish.
        
        Args:
            chat_id: Guruh ID
            user_id: Foydalanuvchi ID
            
        Returns:
            Foydalanuvchi ma'lumotlari yoki None
        """
        key = self._get_key(chat_id, user_id)
        return self.data.get(key)
    
    def get_all_strikes(self, chat_id: int) -> Dict[int, int]:
        """
        Guruhning barcha strike'larini olish.
        
        Args:
            chat_id: Guruh ID
            
        Returns:
            {user_id: strike_count} dict
        """
        result = {}
        prefix = f"{chat_id}_"
        
        for key, value in self.data.items():
            if key.startswith(prefix):
                user_id = int(key.replace(prefix, ''))
                result[user_id] = value.get('strikes', 0)
        
        return result
    
    def get_statistics(self) -> dict:
        """
        Umumiy statistika olish.
        
        Returns:
            Statistika dict
        """
        total_users = len(self.data)
        total_strikes = sum(v.get('strikes', 0) for v in self.data.values())
        
        # Eng ko'p strike olganlar
        top_offenders = sorted(
            self.data.items(),
            key=lambda x: x[1].get('strikes', 0),
            reverse=True
        )[:10]
        
        return {
            'total_users': total_users,
            'total_strikes': total_strikes,
            'top_offenders': [
                {
                    'key': k,
                    'strikes': v.get('strikes', 0),
                    'username': v.get('username'),
                    'first_name': v.get('first_name')
                }
                for k, v in top_offenders
            ]
        }


# Singleton instance
db = StrikeDatabase()
