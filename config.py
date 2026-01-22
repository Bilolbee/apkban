"""
Telegram Anti-APK Security Bot - Konfiguratsiya fayli
"""

import os
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()


class Config:
    """Bot konfiguratsiyasi"""
    
    # ==================== ASOSIY SOZLAMALAR ====================
    
    # Bot tokeni (BotFather dan olinadi)
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
    
    # Adminlarni istisno qilish
    # True - adminlar APK yuborishi mumkin
    # False - adminlar ham tekshiriladi
    EXCLUDE_ADMINS: bool = os.getenv('EXCLUDE_ADMINS', 'true').lower() == 'true'
    
    # Log darajasi
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # ==================== STRIKE TIZIMI ====================
    
    # Maksimal strike soni (keyin ban)
    MAX_STRIKES: int = 3
    
    # Mute davomiyligi (sekundlarda) - 10 daqiqa
    MUTE_DURATION: int = 600
    
    # Strike ma'lumotlar fayli
    STRIKES_DB_FILE: str = 'strikes.json'
    
    # ==================== XABARLAR ====================
    
    # Ogohlantirish xabari (1-strike)
    WARNING_MESSAGE: str = (
        "⚠️ <b>Xavfsizlik ogohlantirishi!</b>\n\n"
        "📛 APK fayllar bu guruhda <b>taqiqlangan</b>.\n"
        "🔒 Xavfsizlik sababli APK fayl o'chirildi.\n\n"
        "📊 <b>Strike:</b> {strike}/{max_strike}\n\n"
        "⚡ <i>Keyingi qoidabuzarlik jazolanadi!</i>"
    )
    
    # Mute xabari (2-strike)
    MUTE_MESSAGE: str = (
        "🔇 <b>Siz 10 daqiqaga mute qilindingiz!</b>\n\n"
        "📛 Sabab: APK fayl yuborish (2-marta)\n"
        "📊 <b>Strike:</b> {strike}/{max_strike}\n\n"
        "⚠️ <i>Keyingi qoidabuzarlik - BAN!</i>"
    )
    
    # Ban xabari (3-strike)
    BAN_MESSAGE: str = (
        "🚫 <b>Foydalanuvchi guruhdan chiqarildi!</b>\n\n"
        "👤 Foydalanuvchi: {user_mention}\n"
        "📛 Sabab: APK fayl yuborish (3-marta)\n\n"
        "🔒 <i>Guruh xavfsizligi ta'minlandi.</i>"
    )
    
    # Admin istisno xabari (log uchun)
    ADMIN_EXEMPT_LOG: str = "Admin {username} APK yubordi - istisno qilindi"
    
    # Private chat xabari
    PRIVATE_CHAT_MESSAGE: str = (
        "👋 Salom!\n\n"
        "🤖 Men <b>Anti-APK Security Bot</b>man.\n\n"
        "🔒 Mening vazifam guruhlarni xavfli APK fayllardan himoyalash.\n\n"
        "📌 <b>Qanday ishlaydi?</b>\n"
        "• Guruhga qo'shing\n"
        "• Admin huquqi bering (xabar o'chirish, ban qilish)\n"
        "• APK fayllar avtomatik o'chiriladi\n\n"
        "⚠️ <i>Men faqat guruh va superguruhlarla ishlayman.</i>"
    )
    
    # ==================== APK ANIQLASH ====================
    
    # APK fayl kengaytmalari
    APK_EXTENSIONS: tuple = ('.apk', '.xapk', '.apks', '.apkm')
    
    @classmethod
    def validate(cls) -> bool:
        """Konfiguratsiyani tekshirish"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN .env faylida ko'rsatilmagan!")
        return True
