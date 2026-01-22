"""
🛡️ Telegram Anti-APK Security Bot
================================

Telegram guruhlarini xavfli APK fayllardan himoyalash uchun bot.

Asosiy funksiyalar:
- APK fayllarni avtomatik aniqlash va o'chirish
- Strike tizimi (ogohlantirish → mute → ban)
- Adminlarni istisno qilish
- Batafsil logging

Muallif: Anti-APK Security Bot
Versiya: 1.0.0
"""

import logging
from datetime import datetime, timedelta
from telegram import Update, ChatPermissions, User
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram.error import BadRequest, Forbidden, TelegramError
from telegram.constants import ParseMode

from config import Config
from database import StrikeDatabase

# ==================== LOGGING SOZLASH ====================

logging.basicConfig(
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger('AntiAPKBot')

# Telegram kutubxonasi loglarini kamaytirish
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

# ==================== DATABASE ====================

db = StrikeDatabase(Config.STRIKES_DB_FILE)

# ==================== YORDAMCHI FUNKSIYALAR ====================


async def is_user_admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int
) -> bool:
    """
    Foydalanuvchi admin yoki creator ekanligini tekshirish.
    
    Args:
        update: Telegram update
        context: Bot context
        user_id: Tekshiriladigan foydalanuvchi ID
        
    Returns:
        True agar admin/creator, False aks holda
    """
    try:
        chat_id = update.effective_chat.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except TelegramError as e:
        logger.error(f"Admin tekshirishda xato: {e}")
        return False


async def is_bot_admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> bool:
    """
    Bot adminligini tekshirish.
    
    Args:
        update: Telegram update
        context: Bot context
        
    Returns:
        True agar bot admin, False aks holda
    """
    try:
        chat_id = update.effective_chat.id
        bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
        return bot_member.status == 'administrator'
    except TelegramError as e:
        logger.error(f"Bot adminligini tekshirishda xato: {e}")
        return False


def get_user_mention(user: User) -> str:
    """
    Foydalanuvchi mention yaratish.
    
    Args:
        user: Telegram User object
        
    Returns:
        HTML formatdagi mention
    """
    name = user.first_name or "Foydalanuvchi"
    return f'<a href="tg://user?id={user.id}">{name}</a>'


def is_apk_file(file_name: str) -> bool:
    """
    Fayl APK ekanligini tekshirish.
    
    Args:
        file_name: Fayl nomi
        
    Returns:
        True agar APK, False aks holda
    """
    if not file_name:
        return False
    
    file_name_lower = file_name.lower()
    
    # Kengaytma bilan tugashini tekshirish
    for ext in Config.APK_EXTENSIONS:
        if file_name_lower.endswith(ext):
            return True
        # Fayl nomi ichida .apk borligini tekshirish (masalan: game.apk.zip)
        if ext in file_name_lower:
            return True
    
    return False


# ==================== STRIKE AKSIYALARI ====================


async def apply_warning(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    strike_count: int
) -> None:
    """
    1-strike: Faqat ogohlantirish yuborish.
    """
    try:
        message = Config.WARNING_MESSAGE.format(
            strike=strike_count,
            max_strike=Config.MAX_STRIKES
        )
        await update.effective_chat.send_message(
            text=message,
            parse_mode=ParseMode.HTML,
            reply_to_message_id=None
        )
        logger.info(f"Ogohlantirish yuborildi: {user.username or user.id}")
    except TelegramError as e:
        logger.error(f"Ogohlantirish yuborishda xato: {e}")


async def apply_mute(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    strike_count: int
) -> None:
    """
    2-strike: Foydalanuvchini 10 daqiqaga mute qilish.
    """
    try:
        chat_id = update.effective_chat.id
        until_date = datetime.now() + timedelta(seconds=Config.MUTE_DURATION)
        
        # Mute qilish
        permissions = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False
        )
        
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user.id,
            permissions=permissions,
            until_date=until_date
        )
        
        # Xabar yuborish
        message = Config.MUTE_MESSAGE.format(
            strike=strike_count,
            max_strike=Config.MAX_STRIKES
        )
        await update.effective_chat.send_message(
            text=message,
            parse_mode=ParseMode.HTML
        )
        
        logger.info(
            f"Foydalanuvchi mute qilindi: {user.username or user.id} "
            f"({Config.MUTE_DURATION} sekund)"
        )
        
    except BadRequest as e:
        logger.error(f"Mute qilishda xato (huquq yo'q?): {e}")
    except TelegramError as e:
        logger.error(f"Mute qilishda xato: {e}")


async def apply_ban(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    strike_count: int
) -> None:
    """
    3-strike: Foydalanuvchini guruhdan chiqarish (ban).
    """
    try:
        chat_id = update.effective_chat.id
        
        # Ban qilish
        await context.bot.ban_chat_member(
            chat_id=chat_id,
            user_id=user.id
        )
        
        # Strike'larni tozalash
        db.reset_strikes(chat_id, user.id)
        
        # Xabar yuborish
        message = Config.BAN_MESSAGE.format(
            user_mention=get_user_mention(user),
            strike=strike_count,
            max_strike=Config.MAX_STRIKES
        )
        await update.effective_chat.send_message(
            text=message,
            parse_mode=ParseMode.HTML
        )
        
        logger.warning(
            f"Foydalanuvchi BAN qilindi: {user.username or user.id} "
            f"(guruh: {chat_id})"
        )
        
    except BadRequest as e:
        logger.error(f"Ban qilishda xato (huquq yo'q?): {e}")
    except TelegramError as e:
        logger.error(f"Ban qilishda xato: {e}")


# ==================== ASOSIY HANDLERLAR ====================


async def handle_document(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Document (fayl) xabarlarini tekshirish va APK bo'lsa o'chirish.
    """
    # Faqat group va supergroup uchun
    if update.effective_chat.type not in ['group', 'supergroup']:
        return
    
    message = update.message
    
    if not message or not message.document:
        return
    
    document = message.document
    file_name = document.file_name or ""
    
    # APK tekshirish
    if not is_apk_file(file_name):
        return
    
    user = message.from_user
    chat_id = message.chat_id
    
    logger.info(
        f"APK aniqlandi: {file_name} | "
        f"Foydalanuvchi: {user.username or user.id} | "
        f"Guruh: {chat_id}"
    )
    
    # Admin tekshirish
    if Config.EXCLUDE_ADMINS:
        if await is_user_admin(update, context, user.id):
            logger.info(Config.ADMIN_EXEMPT_LOG.format(
                username=user.username or user.id
            ))
            return
    
    # Xabarni o'chirish
    try:
        await message.delete()
        logger.info(f"APK xabar o'chirildi: {file_name}")
    except BadRequest as e:
        logger.error(f"Xabarni o'chirishda xato: {e}")
        return
    except Forbidden as e:
        logger.error(f"Xabarni o'chirish taqiqlangan: {e}")
        return
    
    # Strike qo'shish
    strike_count = db.add_strike(
        chat_id=chat_id,
        user_id=user.id,
        username=user.username,
        first_name=user.first_name
    )
    
    # Strike aksiyalari
    if strike_count >= Config.MAX_STRIKES:
        # 3-strike: BAN
        await apply_ban(update, context, user, strike_count)
    elif strike_count == 2:
        # 2-strike: MUTE
        await apply_mute(update, context, user, strike_count)
    else:
        # 1-strike: WARNING
        await apply_warning(update, context, user, strike_count)


async def handle_private_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Private chat xabarlariga javob berish.
    """
    if update.effective_chat.type != 'private':
        return
    
    await update.message.reply_text(
        text=Config.PRIVATE_CHAT_MESSAGE,
        parse_mode=ParseMode.HTML
    )


async def cmd_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /start buyrug'i handleri.
    """
    if update.effective_chat.type == 'private':
        await update.message.reply_text(
            text=Config.PRIVATE_CHAT_MESSAGE,
            parse_mode=ParseMode.HTML
        )
    else:
        # Guruhda /start
        if await is_bot_admin(update, context):
            await update.message.reply_text(
                "✅ <b>Bot faol!</b>\n\n"
                "🛡️ Guruh APK fayllardan himoyalangan.",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                "⚠️ <b>Botga admin huquqi bering!</b>\n\n"
                "Kerakli huquqlar:\n"
                "• Xabarlarni o'chirish\n"
                "• Foydalanuvchilarni cheklash\n"
                "• Foydalanuvchilarni ban qilish",
                parse_mode=ParseMode.HTML
            )


async def cmd_stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /stats buyrug'i - strike statistikasi (faqat adminlar uchun).
    """
    if update.effective_chat.type not in ['group', 'supergroup']:
        return
    
    # Admin tekshirish
    if not await is_user_admin(update, context, update.effective_user.id):
        await update.message.reply_text(
            "⚠️ Bu buyruq faqat adminlar uchun!"
        )
        return
    
    chat_id = update.effective_chat.id
    strikes = db.get_all_strikes(chat_id)
    
    if not strikes:
        await update.message.reply_text(
            "📊 <b>Statistika</b>\n\n"
            "✅ Hech qanday qoidabuzarlik yo'q!",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Statistika shakllantirish
    text = "📊 <b>Strike Statistikasi</b>\n\n"
    
    for user_id, count in sorted(strikes.items(), key=lambda x: x[1], reverse=True):
        info = db.get_user_info(chat_id, user_id)
        name = info.get('username') or info.get('first_name') or str(user_id)
        text += f"• {name}: {count} strike\n"
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_resetstrike(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /resetstrike [user_id] - Strike'larni tozalash (adminlar uchun).
    """
    if update.effective_chat.type not in ['group', 'supergroup']:
        return
    
    # Admin tekshirish
    if not await is_user_admin(update, context, update.effective_user.id):
        await update.message.reply_text(
            "⚠️ Bu buyruq faqat adminlar uchun!"
        )
        return
    
    # Reply qilingan xabar bilan
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_id = target_user.id
    elif context.args and context.args[0].isdigit():
        target_id = int(context.args[0])
    else:
        await update.message.reply_text(
            "❓ <b>Foydalanish:</b>\n"
            "• Xabarga reply qilib /resetstrike\n"
            "• /resetstrike 123456789",
            parse_mode=ParseMode.HTML
        )
        return
    
    chat_id = update.effective_chat.id
    
    if db.reset_strikes(chat_id, target_id):
        await update.message.reply_text(
            f"✅ Strike'lar tozalandi: {target_id}",
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(
            f"ℹ️ Bu foydalanuvchida strike yo'q.",
            parse_mode=ParseMode.HTML
        )


async def cmd_help(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /help buyrug'i.
    """
    help_text = (
        "🛡️ <b>Anti-APK Security Bot</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        
        "📌 <b>Asosiy funksiyalar:</b>\n"
        "• APK fayllarni avtomatik o'chirish\n"
        "• Strike tizimi bilan jazo\n"
        "• Adminlarni istisno qilish\n\n"
        
        "⚡ <b>Strike tizimi:</b>\n"
        "1️⃣ 1-strike → Ogohlantirish\n"
        "2️⃣ 2-strike → 10 daqiqa mute\n"
        "3️⃣ 3-strike → Ban\n\n"
        
        "🔧 <b>Admin buyruqlari:</b>\n"
        "/stats - Strike statistikasi\n"
        "/resetstrike - Strike tozalash\n"
        "/help - Yordam\n\n"
        
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔒 <i>Guruhingiz xavfsiz!</i>"
    )
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)


# ==================== ERROR HANDLER ====================


async def error_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Global error handler.
    """
    logger.error(f"Xatolik yuz berdi: {context.error}")
    
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring."
            )
        except Exception:
            pass


# ==================== MAIN ====================


def main() -> None:
    """
    Botni ishga tushirish.
    """
    # Konfiguratsiyani tekshirish
    try:
        Config.validate()
    except ValueError as e:
        logger.critical(f"Konfiguratsiya xatosi: {e}")
        print(f"\n❌ XATO: {e}")
        print("📌 .env faylini yarating va BOT_TOKEN ni kiriting.\n")
        return
    
    logger.info("=" * 50)
    logger.info("🛡️ Anti-APK Security Bot ishga tushmoqda...")
    logger.info("=" * 50)
    
    # Application yaratish
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Command handlerlar
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("stats", cmd_stats))
    application.add_handler(CommandHandler("resetstrike", cmd_resetstrike))
    
    # Document handler (APK tekshirish)
    application.add_handler(
        MessageHandler(
            filters.Document.ALL & filters.ChatType.GROUPS,
            handle_document
        )
    )
    
    # Private chat handler
    application.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & ~filters.COMMAND,
            handle_private_message
        )
    )
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Botni ishga tushirish
    logger.info("✅ Bot muvaffaqiyatli ishga tushdi!")
    logger.info(f"📊 Adminlarni istisno qilish: {Config.EXCLUDE_ADMINS}")
    logger.info(f"⚡ Max strikes: {Config.MAX_STRIKES}")
    logger.info(f"🔇 Mute davomiyligi: {Config.MUTE_DURATION} sekund")
    
    print("\n" + "=" * 50)
    print("  ANTI-APK SECURITY BOT")
    print("=" * 50)
    print("[OK] Bot muvaffaqiyatli ishga tushdi!")
    print("[*] To'xtatish uchun: Ctrl+C")
    print("=" * 50 + "\n")
    
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == '__main__':
    main()
