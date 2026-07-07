require('dotenv').config();
const { Telegraf, Markup } = require('telegraf');
const OpenAI = require('openai');

// Configuration
const BOT_TOKEN = process.env.BOT_TOKEN; // .env file se lein
const OPENAI_API_KEY = process.env.OPENAI_API_KEY; // .env file se lein

if (!BOT_TOKEN || !OPENAI_API_KEY) {
    console.error('ERROR: Please set BOT_TOKEN and OPENAI_API_KEY in .env file');
    process.exit(1);
}

const bot = new Telegraf(8965822236:AAFZMaabmqiGFKiKSNtZVKpX3RrMX4XM-Uk);
const openai = new OpenAI({ sk-abcdef1234567890abcdef1234567890abcdef12 });

// Bot ka System Prompt (Taaki bot ka behavior set rahe)
const systemPrompt = "You are a friendly, helpful, and talking Telegram bot named 'Leo'. You converse in the same language the user uses (Urdu/English mix). Keep responses concise and engaging.";

// 1. Welcome Message (Jab user /start karega)
bot.start(async (ctx) => {
    const userName = ctx.message.from.first_name;
    const welcomeText = `Assalam-o-Alaikum ${userName}! 👋\n\nMera naam Leo hai. Main ek talking bot hoon.\nMujhse kuch bhi pooch sakte hain ya bas chat kar sakte hain! \n\nKaise shuru karein? Bas neeche likhna shuru karein.`;
    
    await ctx.reply(welcomeText, Markup.keyboard([
        ['Poochein', 'Chat Karein'],
        ['Help']
    ]).resize());
});

// 2. Chatting Logic (Talking Feature)
bot.on('text', async (ctx) => {
    const userText = ctx.message.text;
    const chatId = ctx.chat.id;

    // Agar user ne /start nahi kiya tha, toh pehle welcome nahi bhejenge, seedha reply karenge
    
    await ctx.reply("Thinking..."); // Typing indicator

    try {
        // OpenAI se response lena
        const completion = await openai.chat.completions.create({
            model: "gpt-3.5-turbo",
            messages: [
                { role: "system", content: systemPrompt },
                { role: "user", content: userText }
            ],
            temperature: 0.7, // Thoda creative aur natural response ke liye
        });

        const botReply = completion.choices.message.content;

        // "Thinking..." message ko delete karke original reply bhejna (optional, par better hai)
        // Lekin simple rehne ke liye hum seedha reply bhejenge
        
        await ctx.reply(botReply);

    } catch (error) {
        console.error(error);
        await ctx.reply("Sorry, mere network mein thodi dikkat aa rahi hai. Kripya dobara koshish karein.");
    }
});

// 3. Commands Handling (Help)
bot.command('help', (ctx) => {
    ctx.reply(`
    🤖 **Leo Bot Commands:**
    - /start - Shuruat karein
    - /help - Madad dekhein
    - /stop - Bot band karein
    
    Main AI se baat kar sakta hoon! Kuch bhi likhein.
    `);
});

// Bot ko start karein
bot.launch().then(() => {
    console.log('✅ Bot chal raha hai! Ab Telegram par active hai.');
});

// Graceful Stop
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
