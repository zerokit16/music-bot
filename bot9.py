# bot.py — Новогодняя музыка и Пожелания (только треки, без голосовых)
import asyncio
import sys
import logging

# ИСПРАВЛЕНИЕ ДЛЯ WINDOWS (обязательно!)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8014238819:AAEGayg-VAAKr5KN3Ga_Yro2TeAO2kPRK90"
YOUR_USER_ID = 503015817   # твой ID из @userinfobot (без кавычек!)

logging.basicConfig(level=logging.INFO)
user_category = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_category:
        del user_category[user_id]  # сброс состояния

    keyboard = [
        [KeyboardButton("🎄 Новогодняя")],
        [KeyboardButton("💌 Пожелания")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
        "🎄 Выберите категорию для отправки музыки:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message
    text = message.text

    # Выбор категории
    if text in ["🎄 Новогодняя", "💌 Пожелания"]:
        user_category[user_id] = text
        await message.reply_text(
            f"Вы выбрали: <b>{text}</b>\n\n"
            "📎 Прикрепите <b>музыкальный файл</b> (MP3, WAV и т.п.) через значок скрепки.\n"
            "❗️<b>Голосовые сообщения не принимаются!</b>",
            parse_mode="HTML"
        )
        return

    # Принимаем ТОЛЬКО аудиофайлы (НЕ голосовые!)
    if message.audio or (message.document and message.document.mime_type and 'audio' in message.document.mime_type):
        category = user_category.get(user_id)
        if not category:
            await message.reply_text("Сначала выберите категорию через /start")
            return

        del user_category[user_id]

        user = update.effective_user
        username = f"@{user.username}" if user.username else ""
        full_name = user.full_name or "Аноним"
        info_text = f"{category} от {full_name} {username}".strip()

        try:
            await context.bot.send_message(chat_id=YOUR_USER_ID, text=info_text)
            await context.bot.forward_message(
                chat_id=YOUR_USER_ID,
                from_chat_id=message.chat_id,
                message_id=message.message_id
            )
            await message.reply_text("✅ Музыка успешно отправлена!")
        except Exception as e:
            logging.error(f"Ошибка пересылки: {e}")
            await message.reply_text("❌ Не удалось отправить трек.")
        return

    # Отклоняем голосовые
    if message.voice:
        await message.reply_text("❗️Голосовые не принимаются. Только музыкальные файлы!")
        return

    # Всё остальное
    await message.reply_text(
        "Нажмите /start, чтобы выбрать категорию.\n"
        "Разрешены только музыкальные файлы (MP3, WAV) через скрепку 📎."
    )

async def set_bot_commands(application: Application):
    """Устанавливает команду /start в меню бота"""
    await application.bot.set_my_commands([
        BotCommand("start", "Начать отправку музыки")
    ])

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        filters.TEXT | filters.AUDIO | filters.VOICE | filters.Document.ALL,
        handle_message
    ))

    # Устанавливаем команду в меню
    import asyncio
    asyncio.run(set_bot_commands(app))

    print("✅ Бот запущен. Ждём музыку!")
    app.run_polling()

if __name__ == "__main__":
    main()