import json
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

TOKEN = os.getenv("BOT_TOKEN")

with open("questions.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

sessions = {}

async def start(update: Update, context):
    keyboard = [[InlineKeyboardButton("Start Quiz", callback_data="begin")]]
    await update.message.reply_text(
        "Welcome to Bihar CHO OBG Quiz!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def send_question(query, user_id):
    s = sessions[user_id]
    if s["index"] >= len(s["questions"]):
        await query.edit_message_text(
            f"Quiz complete! Score: {s['score']}/{len(s['questions'])}"
        )
        return

    q = s["questions"][s["index"]]
    keyboard = [
        [InlineKeyboardButton(f"{k}. {v}", callback_data=f"ans_{k}")]
        for k, v in q["options"].items()
    ]
    await query.edit_message_text(
        f"Q{q['number']}. {q['question']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def quiz_button(update: Update, context):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id

    if query.data == "begin":
        sessions[uid] = {
            "questions": random.sample(QUESTIONS, min(50, len(QUESTIONS))),
            "index": 0,
            "score": 0
        }
        await send_question(query, uid)

    elif query.data.startswith("ans_") and uid in sessions:
        s = sessions[uid]
        q = s["questions"][s["index"]]
        ans = query.data.replace("ans_", "")
        if ans == q["answer"]:
            s["score"] += 1
            result = "Correct!"
        else:
            result = f"Wrong! Correct answer: {q['answer']}"

        s["index"] += 1
        if s["index"] < len(s["questions"]):
            await query.edit_message_text(result)
            await send_question(query, uid)
        else:
            await query.edit_message_text(
                f"{result}\nQuiz complete! Score: {s['score']}/{len(s['questions'])}"
            )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(quiz_button))
    app.run_polling()

if __name__ == "__main__":
    main()
