import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ==========================================
# НАСТРОЙКИ
# ==========================================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Добавь переменную окружения.")

logging.basicConfig(level=logging.INFO)

# Папки для файлов
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# ОБРАБОТЧИКИ КОМАНД
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Привет! Я бот для быстрого монтажа рилсов.\n\n"
        "📸 Отправь мне фото или видео\n"
        "🎵 Я сам подберу музыку\n"
        "🚀 Напиши /reel — и я соберу рилс"
    )

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_folder = os.path.join(UPLOAD_DIR, user_id)
    os.makedirs(user_folder, exist_ok=True)

    # Фото
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        ext = "jpg"
    # Видео
    elif update.message.video:
        file = await update.message.video.get_file()
        ext = "mp4"
    else:
        await update.message.reply_text("❌ Пожалуйста, отправь фото или видео.")
        return

    file_path = os.path.join(user_folder, f"media_{len(os.listdir(user_folder))}.{ext}")
    await file.download_to_drive(file_path)

    await update.message.reply_text(f"✅ Файл сохранён! Всего загружено: {len(os.listdir(user_folder))}")

async def reel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_folder = os.path.join(UPLOAD_DIR, user_id)

    if not os.listdir(user_folder):
        await update.message.reply_text("❌ Сначала загрузи фото или видео!")
        return

    await update.message.reply_text("⏳ Начинаю монтаж... Это займёт минуту.")

    # 🔥 ВСТАВЬ СЮДА ВЫЗОВ montage.py
    # Сейчас просто заглушка

    await update.message.reply_text("🎉 Готово! Вот твой рилс (пока заглушка).")
    # await update.message.reply_video(open("output/reel.mp4", "rb"))

# ==========================================
# ЗАПУСК БОТА
# ==========================================
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reel", reel))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))

    print("✅ Бот запущен...")
    app.run_polling()