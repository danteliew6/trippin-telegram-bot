from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Dispatcher, ConversationHandler
from config import bot, states
from file_service import handle_file_upload
# from purchase_service import add_purchase
from commands import start, upload_documents, cancel_upload, select_trip_command, cancel, create_trip_command
from handlers import handle_trip_selection, handle_trip_creation


dispatcher = Dispatcher(bot, None, workers=1)
dispatcher.add_handler(CommandHandler("start", start))
# Select Trip Conversation
select_trip_handler = ConversationHandler(
        entry_points=[CommandHandler("select_trip", select_trip_command)],
        states={
            states['SELECTING_TRIP']: [MessageHandler(Filters.text & ~Filters.command, handle_trip_selection)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
        # run_async=True
    )
dispatcher.add_handler(select_trip_handler)

create_trip_handler = ConversationHandler(
        entry_points=[CommandHandler("create_trip", create_trip_command)],
        states={
            states['CREATE_TRIP']: [MessageHandler(Filters.text & ~Filters.command, handle_trip_creation)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
        # run_async=True
    )
dispatcher.add_handler(create_trip_handler)

dispatcher.add_handler(CommandHandler("upload_documents", upload_documents))
dispatcher.add_handler(CommandHandler("cancel_upload", cancel_upload))
# dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, add_purchase))
dispatcher.add_handler(MessageHandler(Filters.document | Filters.photo, handle_file_upload))

# Webhook handler for Telegram updates
def telegram_webhook(request):
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return "OK", 200