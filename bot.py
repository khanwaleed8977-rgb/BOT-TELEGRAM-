import logging
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# ---------- ENVIRONMENT VARIABLES ----------
BOT_TOKEN = os.getenv("8965822236:AAFZMaabmqiGFKiKSNtZVKpX3RrMX4XM-Uk")
GEMINI_API_KEY = os.getenv("AQ.Ab8RN6KCY9TL3bix9bATctLj_hii7qSCdwvsbRLTh_11fZc4Gw")

# ---------- GEMINI AI SETUP ----------
AI_ENABLED = True
AI_AVAILABLE = False

try:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    AI_AVAILABLE = True
    print("✅ Gemini AI ready!")
except Exception as e:
    print(f"⚠️ Gemini error: {e}")

logging.basicConfig(level=logging.INFO)

# ---------- WELCOME COMMAND ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("💬 Chat Now", callback_data="chat")],
        [InlineKeyboardButton("👤 About Me", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 **Assalam o Alaikum {user.first_name}!**\n\n"
        f"🤖 Main ek AI bot hoon. Mujhse kuch bhi poochiye!\n"
        f"✨ Features:\n"
        f"• Baat cheet (AI-powered)\n"
        f"• Welcome message\n"
        f"• Buttons ke saath interaction\n\n"
        f"**Neeche buttons se shuru karein:**",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ---------- BUTTON HANDLER ----------
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "chat":
        await query.edit_message_text(
            "💬 **Mujhe kuch likhiye!**\n"
            "Main AI ki madad se jawab doonga.",
            parse_mode="Markdown"
        )
    elif query.data == "about":
        await query.edit_message_text(
            "👤 **About Me**\n\n"
            "• Python + Telegram Bot\n"
            "• AI: Google Gemini\n"
            "• Made with ❤️ in Pakistan",
            parse_mode="Markdown"
        )

# ---------- AI REPLY ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user = update.effective_user
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await asyncio.sleep(0.5)
    
    if AI_AVAILABLE and AI_ENABLED:
        try:
            response = model.generate_content(
                f"You are a friendly assistant. Reply in simple Urdu or English. User said: {user_text}"
            )
            reply_text = response.text[:4000]
        except Exception as e:
            reply_text = f"⚠️ AI error: {str(e)[:100]}\nMujhe maaf karein, kuch aur poochiye."
    else:
        reply_text = (
            f"✨ **{user.first_name}** ne kaha:\n"
            f"`{user_text}`\n\n"
            f"😊 AI API key set karein!"
        )
    
    final_reply = f"🤖 **Bot**: {reply_text}"
    
    await update.message.reply_text(
        final_reply,
        parse_mode="Markdown",
        reply_to_message_id=update.message.message_id
    )

# ---------- HELP COMMAND ----------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 **Help Menu**\n\n"
        "• /start - Welcome message\n"
        "• /help - Yeh menu\n"
        "• Kuch bhi likho - Main jawab doonga\n"
        "• Buttons use karo extra features ke liye",
        parse_mode="Markdown"
    )

# ---------- ERROR HANDLING ----------
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.message:
            await update.message.reply_text("⚠️ Kuch gadbad ho gayi. Dobara try karein!")
    except:
        pass

# ---------- MAIN FUNCTION ----------
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    print("🤖 Bot chal raha hai... Press Ctrl+C to stop")
    print(f"✅ AI Status: {'Enabled' if AI_AVAILABLE and AI_ENABLED else 'Disabled (echo mode)'}")
    
    # YAHAN FIX - run_polling() directly use karo
    app.run_polling()

if __name__ == "__main__":
    main()
