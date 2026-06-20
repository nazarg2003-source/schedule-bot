import os
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from google import genai

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

schedule_context = ""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global schedule_context
    user_message = update.message.text
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    if user_message.startswith("/schedule"):
        schedule_context = user_message.replace("/schedule", "").strip()
        await update.message.reply_text("✅ Расписание сохранено! Теперь спрашивайте что угодно.")
        return

    prompt = f"Текущее время: {now}\n\nРасписание пользователя:\n{schedule_context}\n\nВопрос пользователя: {user_message}\n\nОтвечай кратко и по делу на русском языке."
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    await update.message.reply_text(response.text)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
