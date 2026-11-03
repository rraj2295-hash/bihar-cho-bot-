import json
import os
import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.environ["BOT_TOKEN"]

with open("questions.json", "r", encoding="utf-8") as f:
    QUESTIONS = [
        q for q in json.load(f)
        if q.get("options") and len(q["options"]) > 0
    ]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["quiz"] = random.sample(
        QUESTIONS, min(50, len(QUESTIONS))
    )
    context.user_data["index"] = 0
    context.user_data["score"] = 0

    await update.message.reply_text(
        "Bihar CHO OBG Quiz शुरू करें!\nकुल प्रश्न: "
        + str(len(context.user_data["quiz"]))
    )
    await send_question(update, context)


async def send_question(update, context):
    quiz = context.user_data.get("quiz", [])
    i = context.user_data.get("index", 0)

    if i >= len(quiz):
        score = context.user_data.get("score", 0)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Quiz पूरा हुआ!\nआपका स्कोर: {score}/{len(quiz)}\nफिर से खेलने के लिए /start दबाएँ।"
        )
        return

    q = quiz[i]
    options = q["options"]

    keyboard = [
        [InlineKeyboardButton(
            f"{key}. {value}",
            callback_data=f"ans_{key}"
        )]
        for key, value in options.items()
    ]

    text = f"प्रश्न {i + 1}/{len(quiz)}\n\n{q['question']}"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def quiz_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    quiz = context.user_data.get("quiz", [])
    i = context.user_data.get("index", 0)

    if i >= len(quiz):
        return

    q = quiz[i]
    selected = query.data.replace("ans_", "")
    correct = str(q.get("answer", "")).strip().upper()

    if selected == correct:
        context.user_data["score"] = context.user_data.get("score", 0) + 1
        result = "✅ सही जवाब!"
    else:
        result = f"❌ गलत जवाब। सही उत्तर: {correct}"

    await query.edit_message_text(
        f"{result}\n\nआपका स्कोर: {context.user_data['score']}"
    )

    context.user_data["index"] = i + 1
    await send_question(update, context)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(quiz_button))

    port = int(os.environ.get("PORT", "10000"))
    render_url = os.environ["RENDER_EXTERNAL_URL"]

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=f"{render_url}/{TOKEN}",
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()
