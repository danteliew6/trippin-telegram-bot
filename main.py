from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Dispatcher
from config import bot
from file_service import handle_file_upload
# from purchase_service import add_purchase
from commands import start, upload_documents, cancel_upload




# Webhook handler for Telegram updates
def telegram_webhook(request):
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher = Dispatcher(bot, None, workers=0)
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("upload_documents", upload_documents))
        dispatcher.add_handler(CommandHandler("cancel_upload", cancel_upload))
        # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, add_purchase))
        dispatcher.add_handler(MessageHandler(Filters.document | Filters.photo, handle_file_upload))
        dispatcher.process_update(update)
        return "OK", 200