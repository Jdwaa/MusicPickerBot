import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ==========================================
# ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ
# ==========================================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Добавь переменную окружения.")

logging.basicConfig(level=logging.INFO)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# КОМАНДА /START
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Привет! Я бот для быстрого монтажа рилсов.\n\n"
        "📸 Отправь мне фото или видео\n"
        "🎵 Я сам подберу музыку\n"
        "🚀 Напиши /reel — и я соберу рилс\n\n"
        "🔍 Проверка переменных: /check_env"
    )

# ==========================================
# КОМАНДА /CHECK_ENV
# ==========================================
async def check_env(update: Update, context: ContextTypes.DEFAULT_TYPE):
    env_vars = {
        "BOT_TOKEN": "✅" if os.getenv("BOT_TOKEN") else "❌",
        "HF_TOKEN": "✅" if os.getenv("HF_TOKEN") else "❌",
        "FREESOUND_API_KEY": "✅" if os.getenv("FREESOUND_API_KEY") else "❌",
    }
    message = "🔍 Состояние переменных окружения:\n\n"
    for key, status in env_vars.items():
        message += f"{key}: {status}\n"
    await update.message.reply_text(message)

# ==========================================
# ОБРАБОТЧИК ФАЙЛОВ
# ==========================================
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = str(update.message.from_user.id)
    user_folder = os.path.join(UPLOAD_DIR, user_id)
    os.makedirs(user_folder, exist_ok=True)

    file = None
    ext = None

    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        ext = "jpg"
    elif update.message.video:
        file = await update.message.video.get_file()
        ext = "mp4"
    elif update.message.document:
        doc = update.message.document
        if doc.mime_type and "image" in doc.mime_type:
            file = await doc.get_file()
            ext = "jpg"
        elif doc.mime_type and "video" in doc.mime_type:
            file = await doc.get_file()
            ext = "mp4"
        else:
            await update.message.reply_text("❌ Неподдерживаемый тип файла.")
            return
    else:
        await update.message.reply_text("❌ Отправь фото или видео.")
        return

    if not file or not ext:
        await update.message.reply_text("❌ Не удалось обработать файл.")
        return

    file_path = os.path.join(user_folder, f"media_{len(os.listdir(user_folder))}.{ext}")
    await file.download_to_drive(file_path)

    await update.message.reply_text(f"✅ Файл сохранён! Всего загружено: {len(os.listdir(user_folder))}")

# ==========================================
# КОМАНДА /REEL (пока заглушка)
# ==========================================
async def reel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_folder = os.path.join(UPLOAD_DIR, user_id)

    if not os.path.exists(user_folder) or not os.listdir(user_folder):
        await update.message.reply_text("❌ Сначала загрузи фото или видео!")
        return

    await update.message.reply_text("⏳ Начинаю монтаж... Это займёт минуту.")

    # 🔥 ВСТАВЬ СЮДА ВЫЗОВ montage.py
    # Сейчас просто заглушка

    await update.message.reply_text("🎉 Готово! Вот твой рилс (пока заглушка).")

# ==========================================
# ЗАПУСК БОТА
# ==========================================
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check_env", check_env))
    app.add_handler(CommandHandler("reel", reel))
    app.add_handler(MessageHandler(filters.ATTACHMENT, handle_media))

    print("✅ Бот запущен...")
    app.run_polling()