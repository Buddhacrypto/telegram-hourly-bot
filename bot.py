import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import math

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Get bot token from environment variable
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Merhaba! Ben saat başı bildirim botuyum. '
                                  'Her saat başı size bildirim göndereceğim.')

async def check_time(context: ContextTypes.DEFAULT_TYPE):
    """Check the time and send notification if it's one minute to the next hour (xx:59)."""
    current_time = datetime.now()
    
    # If it's xx:59
    if current_time.minute == 59:
        next_hour = (current_time + timedelta(hours=1)).hour
        message = f"⏰ Dikkat! Saat {next_hour}:00'a 1 dakika kaldı!"
        
        # Send message to all subscribed users
        for chat_id in context.bot_data.get('subscribed_users', set()):
            try:
                await context.bot.send_message(chat_id=chat_id, text=message)
            except Exception as e:
                logging.error(f"Error sending message to {chat_id}: {e}")

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Subscribe the user to hourly notifications."""
    chat_id = update.effective_chat.id
    
    if 'subscribed_users' not in context.bot_data:
        context.bot_data['subscribed_users'] = set()
    
    context.bot_data['subscribed_users'].add(chat_id)
    await update.message.reply_text('Saat başı bildirimlerine başarıyla abone oldunuz!')

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unsubscribe the user from hourly notifications."""
    chat_id = update.effective_chat.id
    
    if 'subscribed_users' in context.bot_data:
        context.bot_data['subscribed_users'].discard(chat_id)
    
    await update.message.reply_text('Saat başı bildirimlerinden başarıyla çıktınız!')

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))

    # Add job to check time every minute
    job_queue = application.job_queue

    # Şu anki zamanı al
    now = datetime.now()
    # Bir sonraki tam dakikaya kadar olan saniye
    seconds_until_next_minute = 60 - now.second

    # Job'u tam dakika başında başlat
    job_queue.run_repeating(check_time, interval=60, first=seconds_until_next_minute)

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 