# 🛡️ Telegram Anti-APK Security Bot

Telegram guruhlarini xavfli APK fayllardan himoyalash uchun professional bot.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Mundarija

- [Xususiyatlar](#-xususiyatlar)
- [O'rnatish](#-ornatish)
- [Konfiguratsiya](#-konfiguratsiya)
- [Ishga tushirish](#-ishga-tushirish)
- [Buyruqlar](#-buyruqlar)
- [Strike Tizimi](#-strike-tizimi)
- [Xavfsizlik](#-xavfsizlik)

---

## ✨ Xususiyatlar

### 🔍 APK Aniqlash
- `.apk`, `.xapk`, `.apks`, `.apkm` fayllarni aniqlash
- Fayl nomi ichida `.apk` borligini tekshirish
- Avtomatik o'chirish

### ⚡ Strike Tizimi
| Strike | Jazo |
|--------|------|
| 1️⃣ 1-marta | Ogohlantirish xabari |
| 2️⃣ 2-marta | 10 daqiqaga mute |
| 3️⃣ 3-marta | Guruhdan ban |

### 🔐 Xavfsizlik
- Faqat guruh/superguruhda ishlaydi
- Private chatlarda ishlamaydi (Telegram API cheklovi)
- Adminlarni istisno qilish imkoniyati
- Barcha hodisalar loglanadi

### 📊 Statistika
- Strike hisobini saqlash
- Admin buyruqlari orqali statistika ko'rish
- Strike'larni tozalash imkoniyati

---

## 🚀 O'rnatish

### 1. Reponi klonlash yoki fayllarni yaratish

```bash
# Papka yaratish
mkdir anti-apk-bot
cd anti-apk-bot
```

### 2. Virtual environment yaratish (tavsiya qilinadi)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 4. Bot yaratish

1. Telegram'da [@BotFather](https://t.me/BotFather) ga o'ting
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting
4. Bot username'ini kiriting
5. **Bot Token**ni nusxalang

### 5. Konfiguratsiya

`env.example.txt` faylini `.env` deb nomini o'zgartiring va tokenni kiriting:

```bash
# Windows
copy env.example.txt .env

# Linux/Mac  
cp env.example.txt .env
```

`.env` faylini tahrirlang:

```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
EXCLUDE_ADMINS=true
LOG_LEVEL=INFO
```

---

## ⚙️ Konfiguratsiya

### .env fayli

| O'zgaruvchi | Tavsif | Standart |
|-------------|--------|----------|
| `BOT_TOKEN` | BotFather'dan olingan token | **Majburiy** |
| `EXCLUDE_ADMINS` | Adminlarni istisno qilish | `true` |
| `LOG_LEVEL` | Log darajasi (DEBUG, INFO, WARNING, ERROR) | `INFO` |

### config.py'da o'zgartirish mumkin

```python
# Strike tizimi
MAX_STRIKES = 3          # Maksimal strike (keyin ban)
MUTE_DURATION = 600      # Mute davomiyligi (sekundda)

# APK kengaytmalari
APK_EXTENSIONS = ('.apk', '.xapk', '.apks', '.apkm')
```

---

## 🏃 Ishga tushirish

```bash
python bot.py
```

Muvaffaqiyatli ishga tushganda quyidagini ko'rasiz:

```
==================================================
🛡️  ANTI-APK SECURITY BOT
==================================================
✅ Bot muvaffaqiyatli ishga tushdi!
📌 To'xtatish uchun: Ctrl+C
==================================================
```

---

## 📝 Buyruqlar

### Barcha foydalanuvchilar uchun

| Buyruq | Tavsif |
|--------|--------|
| `/start` | Botni boshlash / holat tekshirish |
| `/help` | Yordam va ma'lumot |

### Faqat adminlar uchun

| Buyruq | Tavsif |
|--------|--------|
| `/stats` | Guruh strike statistikasi |
| `/resetstrike` | Foydalanuvchi strike'larini tozalash |

### /resetstrike ishlatish

```
# Xabarga reply qilib
/resetstrike

# User ID bilan
/resetstrike 123456789
```

---

## ⚡ Strike Tizimi

```
📱 Foydalanuvchi APK yubordi
         │
         ▼
    ┌─────────────┐
    │ 1-STRIKE    │ ──► ⚠️ Ogohlantirish
    └─────────────┘
         │
         ▼
    ┌─────────────┐
    │ 2-STRIKE    │ ──► 🔇 10 daqiqa MUTE
    └─────────────┘
         │
         ▼
    ┌─────────────┐
    │ 3-STRIKE    │ ──► 🚫 BAN
    └─────────────┘
```

Strike ma'lumotlari `strikes.json` faylida saqlanadi.

---

## 🔐 Xavfsizlik

### Bot huquqlari

Botni guruhga qo'shgandan so'ng quyidagi huquqlarni bering:

- ✅ Xabarlarni o'chirish (Delete messages)
- ✅ Foydalanuvchilarni cheklash (Restrict members)
- ✅ Foydalanuvchilarni ban qilish (Ban users)

### Private chat cheklovi

Bot private chatlarda:
- ❌ APK aniqlamaydi
- ❌ Xabar o'chirmaydi
- ℹ️ Faqat ma'lumot beradi

Bu Telegram API cheklovi sababli shunday.

---

## 📁 Fayl tuzilmasi

```
anti-apk-bot/
├── bot.py              # Asosiy bot fayli
├── config.py           # Konfiguratsiya
├── database.py         # Strike database
├── requirements.txt    # Python kutubxonalari
├── .env                # Maxfiy sozlamalar
├── env.example.txt     # .env namunasi
├── strikes.json        # Strike ma'lumotlari (avtomatik)
├── bot.log             # Log fayli (avtomatik)
└── README.md           # Hujjat
```

---

## 🔧 Muammolarni hal qilish

### Bot ishlamayapti

```bash
# Token to'g'riligini tekshiring
# .env faylida:
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

### Xabar o'chirilmayapti

1. Botni guruhga admin qiling
2. "Delete messages" huquqini bering

### Mute/Ban ishlamayapti

1. "Restrict members" huquqini bering
2. "Ban users" huquqini bering

### Log ko'rish

```bash
# Real-time log
tail -f bot.log

# Windows'da
type bot.log
```

---

## 🐳 Docker bilan ishga tushirish (ixtiyoriy)

`Dockerfile` yarating:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

Ishga tushirish:

```bash
docker build -t anti-apk-bot .
docker run -d --name apk-bot --env-file .env anti-apk-bot
```

---

## 📄 Litsenziya

MIT License - Erkin foydalaning!

---

## 🤝 Muallif

Telegram Anti-APK Security Bot

---

**🛡️ Guruhingizni xavfsiz saqlang!**
