import os
import httpx
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

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

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={
                "model": "google/gemma-3-4b-it",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        result = response.json()
        logger.info(f"OpenRouter response: {result}")
        
        if "choices" in result:
            answer = result["choices"][0]["message"]["content"]
        else:
            answer = f"Ошибка: {result.get('error', result)}"

    await update.message.reply_text(answer)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
