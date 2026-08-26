import os
import json
import random
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Token będzie dodany później jako zmienna środowiskowa
TOKEN = os.getenv("BOT_TOKEN")

# Plik z informacjami o ostatnich losowaniach
DATA_FILE = "users.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def get_today():
    return datetime.now().strftime("%Y-%m-%d")


def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎡 ZAKRĘĆ KOŁEM", callback_data="spin")],
        [InlineKeyboardButton("📅 Sprawdź limit", callback_data="limit")]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎡 <b>KOŁO FORTUNY</b> 🎡\n\n"
        "✨ Zakręć kołem i sprawdź, co dzisiaj wylosujesz!\n\n"
        "🎁 Możesz zakręcić <b>raz dziennie</b>.\n"
        "🍀 Powodzenia!"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    today = get_today()

    data = load_data()

    if user_id not in data:
        data[user_id] = {}

    last_spin = data[user_id].get("last_spin")

    # Sprawdzenie, czy użytkownik już dzisiaj losował
    if query.data == "spin":

        if last_spin == today:
            await query.edit_message_text(
                "⏰ <b>JUŻ DZIŚ LOSOWAŁAŚ!</b>\n\n"
                "🎡 Możesz zakręcić ponownie jutro. 💗\n\n"
                "🍀 Powodzenia następnym razem!",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📅 Sprawdź limit", callback_data="limit")]
                ])
            )
            return

        # Nagrody i ich wagi
        prizes = [
            ("🎁 DARMOWY BONUS", 5),
            ("💸 RABAT 20%", 10),
            ("💸 RABAT 10%", 20),
            ("⭐ RABAT 5%", 25),
            ("🍀 SPRÓBUJ SZCZĘŚCIA JUTRO", 40)
        ]

        names = [item[0] for item in prizes]
        weights = [item[1] for item in prizes]

        result = random.choices(names, weights=weights, k=1)[0]

        # Zapisujemy dzisiejsze losowanie
        data[user_id]["last_spin"] = today
        data[user_id]["last_result"] = result

        save_data(data)

        await query.edit_message_text(
            "🎡 <b>KOŁO ZAKRĘCONE!</b> 🎡\n\n"
            f"✨ Wylosowałaś:\n\n"
            f"<b>{result}</b>\n\n"
            "📅 Kolejne losowanie będzie dostępne jutro.\n"
            "🍀 Powodzenia!",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📅 Sprawdź limit", callback_data="limit")]
            ])
        )

    elif query.data == "limit":

        if last_spin == today:
            text = (
                "📅 <b>TWÓJ LIMIT NA DZIŚ</b>\n\n"
                "🔴 Losowanie zostało już wykorzystane.\n\n"
                "🎡 Wróć jutro, aby zakręcić ponownie!"
            )
        else:
            text = (
                "📅 <b>TWÓJ LIMIT</b>\n\n"
                "🟢 Możesz dzisiaj zakręcić kołem!\n\n"
                "👇 Kliknij przycisk poniżej."
            )

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎡 ZAKRĘĆ KOŁEM", callback_data="spin")],
                [InlineKeyboardButton("🏠 MENU", callback_data="menu")]
            ])
        )

    elif query.data == "menu":

        await query.edit_message_text(
            "🎡 <b>KOŁO FORTUNY</b> 🎡\n\n"
            "✨ Zakręć kołem i sprawdź swoje szczęście!\n\n"
            "📅 Jedno losowanie dziennie.",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )


def run_bot():
    if not TOKEN:
        raise ValueError("Brak zmiennej BOT_TOKEN.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🎡 Bot działa!")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
