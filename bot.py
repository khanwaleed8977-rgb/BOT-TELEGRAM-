import logging
import asyncio
import os
import sys
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# ============================================
#  TOKEN SETUP
# ============================================

# Render se environment variable lo
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Agar Render se nahi mila toh direct dalo (testing)
if not BOT_TOKEN:
    BOT_TOKEN = "8965822236:AAFZMaabmqiGFKiKSNtZVKpX3RrMX4XM-Uk"  # APNA TOKEN

if not BOT_TOKEN or len(BOT_TOKEN) < 10:
    print(" ERROR: Valid Bot Token nahi mila!")
    sys.exit(1)

print(f" Token Loaded: {BOT_TOKEN[:15]}...")

# ============================================
#  GEMINI AI SETUP - FIXED LINE
# ============================================

# YAHAN FIX KARO - SIRF "GEMINI_API_KEY" LIKHO
GEMINI_API_KEY = os.getenv("AQ.Ab8RN6KCY9TL3bix9bATctLj_hii7qSCdwvsbRLTh_11fZc4Gw")  # <-- YEH SAHI HAI

AI_AVAILABLE = False

try:
    if GEMINI_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        AI_AVAILABLE = True
        print(" Gemini AI Enabled!")
    else:
        print(" Gemini disabled - Echo mode active")
except Exception as e:
    print(f" Gemini setup error: {e}")

# ============================================
#  LOGGING
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
#  START COMMAND
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    keyboard = [
        [InlineKeyboardButton(" AI Chat", callback_data="chat")],
        [InlineKeyboardButton(" About Bot", callback_data="about")],
        [InlineKeyboardButton(" My Profile", callback_data="profile")],
        [InlineKeyboardButton(" Date & Time", callback_data="time")],
        [InlineKeyboardButton(" Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = (
        f" **Assalam o Alaikum {user.first_name}!**\n\n"
        f" **Welcome to Smart Bot**\n"
        f"\n\n"
        f" **Features:**\n"
        f"•  AI Powered Chat\n"
        f"•  User Profile View\n"
        f"•  Date & Time\n"
        f"•  Interactive Buttons\n\n"
        f" **Neeche se option select karein:**"
    )
    
    await update.message.reply_text(
        welcome_msg,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ============================================
#  BUTTON HANDLERS
# ============================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    
    if query.data == "chat":
        await query.edit_message_text(
            " **AI Chat Mode**\n\n"
            "Mujhe kuch bhi likhiye, main jawab doonga!\n"
            " Type your message below:",
            parse_mode="Markdown"
        )
    
    elif query.data == "about":
        about_text = (
            " **About This Bot**\n\n"
            "•  **Name:** Smart Bot\n"
            "•  **Language:** Python\n"
            "•  **Library:** python-telegram-bot\n"
            "•  **AI:** Google Gemini\n"
            "•  **Host:** Render.com\n"
            "•  **Made with **\n\n"
            f" Server Time: {datetime.now().strftime('%I:%M %p')}"
        )
        await query.edit_message_text(
            about_text,
            parse_mode="Markdown"
        )
    
    elif query.data == "profile":
        profile_text = (
            f" **User Profile**\n\n"
            f"• **Name:** {user.first_name}\n"
            f"• **ID:** `{user.id}`\n"
            f"• **Username:** @{user.username if user.username else 'Not Set'}\n"
            f"• **Bot:** Active "
        )
        await query.edit_message_text(
            profile_text,
            parse_mode="Markdown"
        )
    
    elif query.data == "time":
        current_time = datetime.now().strftime("%A, %B %d, %Y\n %I:%M:%S %p")
        await query.edit_message_text(
            f" **Current Date & Time**\n\n"
            f"`{current_time}`\n\n"
            f" Pakistan Time (GMT+5)",
            parse_mode="Markdown"
        )
    
    elif query.data == "help":
        help_text = (
            " **Help & Commands**\n\n"
            "• /start - Show Main Menu\n"
            "• /help - This Message\n"
            "• /about - About Bot\n"
            "• /time - Current Time\n\n"
            " **Buttons use karein** for more options!"
        )
        await query.edit_message_text(
            help_text,
            parse_mode="Markdown"
        )

# ============================================
#  AI CHAT HANDLER
# ============================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user = update.effective_user
    
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, 
        action="typing"
    )
    await asyncio.sleep(0.3)
    
    if AI_AVAILABLE:
        try:
            prompt = f"You are a friendly Pakistani assistant. Reply in simple Urdu or English. User said: {user_text}"
            response = model.generate_content(prompt)
            reply_text = response.text[:4000]
        except Exception as e:
            reply_text = f" AI Error: {str(e)[:100]}"
    else:
        reply_text = (
            f" **{user.first_name}** said:\n"
            f"`{user_text}`\n\n"
            f" **Bot Reply:**\n"
            f"Namaste! Main AI mode mein nahi hoon.\n"
            f"Setup Gemini API key for smart replies!"
        )
    
    await asyncio.sleep(0.2)
    await update.message.reply_text(
        f" {reply_text}",
        parse_mode="Markdown",
        reply_to_message_id=update.message.message_id
    )

# ============================================
#  COMMAND HANDLERS
# ============================================

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        " **Smart Bot v1.0**\n\nPython Telegram Bot with AI features!\nMade for Pakistan ",
        parse_mode="Markdown"
    )

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_time = datetime.now().strftime("%I:%M:%S %p")
    await update.message.reply_text(
        f" Current Time: `{current_time}`",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# ============================================
#  ERROR HANDLER
# ============================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error: {context.error}")
    try:
        if update and hasattr(update, 'message') and update.message:
            await update.message.reply_text(
                " **Error!**\nKuch gadbad ho gayi. Dobara try karein!",
                parse_mode="Markdown"
            )
    except:
        pass

# ============================================
#  MAIN FUNCTION
# ============================================

def main():
    print("=" * 50)
    print(" Starting Smart Bot...")
    print("=" * 50)
    print(f" Token: {BOT_TOKEN[:15]}...")
    print(f" AI Status: {' Enabled' if AI_AVAILABLE else ' Disabled'}")
    print("=" * 50)
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("time", time_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    print(" Bot is running! Press Ctrl+C to stop")
    print("=" * 50)
    
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()
