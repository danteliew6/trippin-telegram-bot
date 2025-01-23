from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Dispatcher
from config import bot
from purchase_service import add_purchase

# Telegram bot command handlers
def start(update: Update, context) -> None:
    update.message.reply_text("Welcome! Send your travel purchase details in the format:\nItem, Cost, Date")



# Webhook handler for Telegram updates
def telegram_webhook(request):
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher = Dispatcher(bot, None, workers=0)
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, add_purchase))
        dispatcher.process_update(update)
        return "OK", 200