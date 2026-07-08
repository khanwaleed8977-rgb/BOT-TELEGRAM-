import os
import telebot
import google.generativeai as genai
import re
import time

# ---------- 🔑 Render Environment Variables ----------
TELEGRAM_BOT_TOKEN = os.environ.get("8965822236:AAFZMaabmqiGFKiKSNtZVKpX3RrMX4XM-Uk")
GEMINI_API_KEY = os.environ.get("AQ.Ab8RN6KCY9TL3bix9bATctLj_hii7qSCdwvsbRLTh_11fZc4Gw")

# Agar keys set nahi hain toh error dikhao
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN set karein Render Environment Variables mein!")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY set karein Render Environment Variables mein!")

# -------------------------------------------------

# 1. Gemini Configure
genai.configure(api_key=GEMINI_API_KEY)

MASTI_PROMPT = """Tum ek masty bhari, sarcastic aur intelligent bot ho.
Har sawaal ka jawab Hinglish mein do, thoda attitude aur mazaak ke saath.
Hamesha apni baat ke end mein relevant emoji daalo. 😎
Agar boring sawaal puche toh interesting bana ke jawab do.
Tumhara naam "Chatty" hai.
Kisi bhi cheez ka jawab do, lekin illegal ya harmful ho toh mana kar do.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=MASTI_PROMPT
)

# 2. Telegram Bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# 3. /start & /help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🤖 **Namaste! Main hoon Chatty - aapka masti bhara AI dost!**\n\n"
        "Mujhe kuch bhi poochiye, main har baat ka jawab doonga.\n"
        "Bas yaad rakhiyega: Main thoda sarcastic hoon! 😜\n\n"
        "Commands:\n"
        "/start - Meri shuruat karein\n"
        "/help - Yeh help dekhein\n"
        "/clear - Meri yaadash mitayein\n\n"
        "Ab boliye, kya poochna hai? 🔥"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

# 4. Chat Memory
user_conversations = {}

@bot.message_handler(func=lambda message: True)
def chat_with_gemini(message):
    user_id = message.from_user.id
    user_text = message.text

    if message.from_user.is_bot:
        return

    bot.send_chat_action(message.chat.id, 'typing')

    try:
        history = user_conversations.get(user_id, [])
        history.append({"role": "user", "parts": [user_text]})

        if len(history) > 10:
            history = history[-10:]

        response = model.generate_content(history)
        reply_text = response.text
        reply_text = re.sub(r'\s+', ' ', reply_text).strip()

        if len(reply_text) > 4000:
            reply_text = reply_text[:4000] + "... (baaki ka jawab lamba hai 😅)"

        bot.reply_to(message, reply_text)
        history.append({"role": "model", "parts": [reply_text]})
        user_conversations[user_id] = history

    except Exception as e:
        error_msg = f"❌ Oops! Kuch gadbad ho gayi. Thodi der baad try karo! 😴\nError: {e}"
        bot.reply_to(message, error_msg)
        print(f"Error: {e}")

@bot.message_handler(commands=['clear'])
def clear_memory(message):
    user_id = message.from_user.id
    if user_id in user_conversations:
        del user_conversations[user_id]
    bot.reply_to(message, "🧹 Meri yaadash saaf kar di gayi! Naye dost ki tarah baat karo! 😂")

# 5. Bot Start
if __name__ == "__main__":
    print("🤖 Chatty Bot chal raha hai...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"Bot restart: {e}")
            time.sleep(5)
