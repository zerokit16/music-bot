# bot.py — с категориями и "кнопкой прикрепления"
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ⚠️ ЗАМЕНИ НА СВОИ ДАННЫЕ (если запускаешь локально)
BOT_TOKEN = "8014238819:AAG6rz-pzr22euc5-KyWgs_DJOTvPj6PZww"
YOUR_USER_ID = 503015817    # твой ID из @userinfobot

logging.basicConfig(level=logging.INFO)

# Храним выбор категории и состояние
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🎧 Личная музыка")],
        [KeyboardButton("🎉 Треки на дискотеку")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "Выберите категорию:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message
    text = message.text

    # Шаг 1: Выбор категории
    if text in ["🎧 Личная музыка", "🎉 Треки на дискотеку"]:
        user_data[user_id] = {"category": text}
        # Показываем "кнопку прикрепления"
        attach_kb = [[KeyboardButton("📎 Прикрепить аудиофайл")]]
        reply_markup = ReplyKeyboardMarkup(attach_kb, resize_keyboard=True, one_time_keyboard=True)
        await message.reply_text(
            f"Вы выбрали: <b>{text}</b>\n\n"
            "Теперь нажмите кнопку ниже, чтобы отправить трек.",
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        return

    # Шаг 2: Нажата "кнопка прикрепления"
    if text == "📎 Прикрепить аудиофайл":
        await message.reply_text(
            "🔊 Чтобы отправить трек:\n"
            "1. Нажмите значок 📎 (скрепка) внизу\n"
            "2. Выберите <b>«Аудио»</b> или <b>«Голосовое сообщение»</b>\n"
            "3. Отправьте файл.\n\n"
            "<i>Текст и другие файлы не принимаются.</i>",
            parse_mode="HTML"
        )
        return

    # Шаг 3: Получение аудио
    if message.audio or message.voice or (message.document and message.document.mime_type and 'audio' in message.document.mime_type):
        if user_id in user_data and "category" in user_data[user_id]:
            category = user_data[user_id]["category"]
            del user_data[user_id]  # сброс состояния

            # Информация об отправителе
            user = update.effective_user
            username = f"@{user.username}" if user.username else ""
            full_name = user.full_name or "Аноним"

            # Отправляем тебе
            label = category
            info_text = f"{label} от {full_name} {username}".strip()
            try:
                await context.bot.send_message(chat_id=YOUR_USER_ID, text=info_text)
                await context.bot.forward_message(
                    chat_id=YOUR_USER_ID,
                    from_chat_id=message.chat_id,
                    message_id=message.message_id
                )
                await message.reply_text("✅ Трек успешно отправлен!")
            except Exception as e:
                logging.error(f"Ошибка: {e}")
                await message.reply_text("❌ Не удалось отправить трек.")
        else:
            await message.reply_text("Сначала выберите категорию через /start")
        return

    # Любое другое сообщение — игнорируем
    await message.reply_text(
        "Пожалуйста, следуйте инструкциям:\n"
        "1. Выберите категорию\n"
        "2. Нажмите «Прикрепить аудиофайл»\n"
        "3. Отправьте аудио через скрепку 📎"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        filters.TEXT | filters.AUDIO | filters.VOICE | filters.Document.AUDIO,
        handle_message
    ))
    print("✅ Бот с категориями и инструкцией запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()