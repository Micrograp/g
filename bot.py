import os
import telebot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env")

bot = telebot.TeleBot(TOKEN)
server_url = os.getenv("SERVER_URL", "http://localhost:5000")

@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    chat_id = message.chat.id
    name = message.from_user.first_name or "Friend"
    gallery_link = f"{server_url}/?uid={chat_id}"

    welcome_text = (
        f"👋 Hello {name}!\n\n"
        f"Your Telegram Chat ID is: `{chat_id}`\n\n"
        f"📸 [Click here to open the Gallery]({gallery_link})\n\n"
        f"Or open this URL in your browser:\n"
        f"`{gallery_link}`"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(content_types=['text', 'photo', 'document'])
def handle_any(message):
    chat_id = message.chat.id
    gallery_link = f"{server_url}/?uid={chat_id}"
    bot.reply_to(
        message,
        f"Your Chat ID is `{chat_id}`.\n\nOpen the gallery here:\n{gallery_link}",
        parse_mode="Markdown"
    )

if __name__ == '__main__':
    bot_info = bot.get_me()
    print("==================================================")
    print(f"🤖 Telegram Bot @{bot_info.username} is running!")
    print(f"➡️  Open Telegram and send /start to @{bot_info.username}")
    print(f"➡️  Gallery URL configured: {server_url}")
    print("==================================================")
    bot.infinity_polling(skip_pending=True)

