# bot.py — Новогодняя vs Пожелания, только музыка (без голосовых!)
import asyncio
import sys
import logging
# ИСПРАВЛЕНИЕ ДЛЯ WINDOWS (обязательно для Python 3.8+)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ⚠️ ЗАМЕНИ НА СВОИ ДАННЫЕ
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
YOUR_USER_ID = int(os.getenv("YOUR_USER_ID"))    # твой ID из @userinfobot

logging.basicConfig(level=logging.INFO)

user_category = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🎄 Новогодняя")],
        [KeyboardButton("💌 Пожелания")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "Выберите категорию для отправки музыки:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message
    text = message.text

    # Шаг 1: Выбор категории
    if text in ["🎄 Новогодняя", "💌 Пожелания"]:
        user_category[user_id] = text
        await message.reply_text(
            f"Вы выбрали: <b>{text}</b>\n\n"
            "📎 Теперь прикрепите <b>музыкальный файл</b> (MP3, WAV и т.п.) через значок скрепки.\n"
            "❗️<b>Голосовые сообщения не принимаются!</b>",
            parse_mode="HTML"
        )
        return

    # Шаг 2: Получение файла — ТОЛЬКО аудиофайлы (НЕ голосовые!)
    if message.audio or (message.document and message.document.mime_type and 'audio' in message.document.mime_type):
        category = user_category.get(user_id)
        if not category:
            await message.reply_text("Сначала выберите категорию через /start")
            return

        # Удаляем состояние
        del user_category[user_id]

        # Информация об отправителе
        user = update.effective_user
        username = f"@{user.username}" if user.username else ""
        full_name = user.full_name or "Аноним"
        info_text = f"{category} от {full_name} {username}".strip()

        try:
            # Отправляем тебе метку
            await context.bot.send_message(chat_id=YOUR_USER_ID, text=info_text)
            # Пересылаем сам файл
            await context.bot.forward_message(
                chat_id=YOUR_USER_ID,
                from_chat_id=message.chat_id,
                message_id=message.message_id
            )
            await message.reply_text("✅ Музыка успешно отправлена!")
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            await message.reply_text("❌ Не удалось отправить музыку.")
        return

    # ❌ Голосовые — отклоняем
    if message.voice:
        await message.reply_text("❗️Голосовые сообщения не принимаются. Пришлите музыкальный файл (MP3 и т.п.).")
        return

    # ❌ Любой другой контент (текст, фото, видео и т.д.)
    await message.reply_text(
        "Только музыкальные файлы!\n"
        "📎 Нажмите скрепку → выберите аудиофайл (MP3, WAV и т.п.).\n"
        "❗️Голосовые не принимаются."
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        filters.TEXT | filters.AUDIO | filters.VOICE | filters.Document.ALL,
        handle_message
    ))
    print("✅ Бот запущен: Новогодняя / Пожелания (только музыка)")
    app.run_polling()

if __name__ == "__main__":
    main()