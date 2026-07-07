import os
import io
import tempfile
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from openai import OpenAI

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("sk-abcdef1234567890abcdef1234567890abcdef12")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Error: Please set BOT_TOKEN and OPENAI_API_KEY in .env file")

# Initialize OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)

# System Prompt for personality
SYSTEM_PROMPT = "You are Leo, a friendly and helpful Telegram bot. You speak Urdu and English mixed (Roman Urdu). Keep responses short, natural, and engaging. If the user speaks in Urdu, reply in Roman Urdu. If in English, reply in English."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message when user sends /start"""
    user_name = update.effective_user.first_name
    welcome_text = f"Assalam-o-Alaikum {user_name}! 👋\n\nMera naam Leo hai. Main ek talking bot hoon!\n\nMujhse chat karein ya **Voice Note** bhejein, main sun kar jawab dunga. 🎤"
    
    await update.message.reply_text(welcome_text)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages and provide AI response"""
    user_text = update.message.text
    chat_id = update.chat.id
    
    # Typing status
    await update.message.chat.send_action(action="typing")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ]
        )
        bot_reply = response.choices.message.content
        await update.message.reply_text(bot_reply)
        
    except Exception as e:
        await update.message.reply_text("Sorry, mere network mein thodi dikkat aa rahi hai. Kripya dobara koshish karein.")
        print(f"Error: {e}")

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice notes: Transcribe -> Chat -> Speak Back"""
    voice_file = update.message.voice
    
    # Typing status
    await update.message.chat.send_action(action="typing")
    
    try:
        # 1. Download voice file
        file_obj = await voice_file.get_file()
        
        # Save to temporary file because OpenAI API needs a file path
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_file:
            temp_path = temp_file.name
            # Download content
            await file_obj.download_to_drive(temp_path)
        
        # 2. Speech-to-Text (Whisper)
        with open(temp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        
        user_text = transcription.text
        print(f"User Voice: {user_text}")
        
        # Cleanup temp file
        os.remove(temp_path)
        
        # 3. Get AI Response
        ai_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ]
        )
        bot_text = ai_response.choices.message.content
        
        # 4. Text-to-Speech (TTS)
        await update.message.chat.send_action(action="record_voice")
        
        speech_response = client.audio.speech.create(
            model="tts-1",
            voice="alloy", # Options: alloy, echo, fable, onyx, nova, shimmer
            input=bot_text
        )
        
        # Convert response to bytes and send as voice note
        audio_bytes = io.BytesIO(speech_response.content)
        audio_bytes.name = "response.mp3"
        
        await update.message.reply_voice(audio_bytes, caption="Ye lo, aapka jawab! 👇")
        
    except Exception as e:
        await update.message.reply_text("Sorry, main aapki awaaz samajh nahi paya. Kripya dobara karein ya text mein likhein.")
        print(f"Voice Error: {e}")
        
    finally:
        # Cleanup if file still exists (safety)
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    🤖 **Leo Bot Features:**
    - 📝 Text chat karein
    - 🎤 Voice note bhejein (Main sun kar audio reply dunga)
    - /start - Shuruat
    - /help - Madad
    """
    await update.message.reply_text(help_text)

if __name__ == '__main__':
    # Build Application
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Text Messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Voice Messages
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    
    print("✅ Bot chal raha hai! Ab Telegram par active hai...")
    application.run_polling()
