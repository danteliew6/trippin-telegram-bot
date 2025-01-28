from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Dispatcher, ConversationHandler, CallbackQueryHandler
from config import bot, states
# from purchase_service import add_purchase
from commands import start, trip_info_command, upload_documents, cancel_upload, select_trip_command, cancel, create_trip_command
from handlers import handle_get_item_info, handle_show_item_info, handle_trip_info_selection, handle_trip_selection, handle_trip_creation, handle_file_upload


dispatcher = Dispatcher(bot, None, workers=1)
dispatcher.add_handler(CommandHandler("start", start))
# Select Trip Conversation
select_trip_handler = ConversationHandler(
        entry_points=[CommandHandler("select_trip", select_trip_command)],
        states={
            states['SELECTING_TRIP']: [
                CallbackQueryHandler(cancel, pattern="^cancel$"),  # Handle "Cancel" button clicks
                CallbackQueryHandler(handle_trip_selection)
                ]

        },
        fallbacks=[CommandHandler("cancel", cancel)]
        # run_async=True
    )
dispatcher.add_handler(select_trip_handler)

create_trip_handler = ConversationHandler(
        entry_points=[CommandHandler("create_trip", create_trip_command)],
        states={
            states['CREATE_TRIP']: [
                MessageHandler(Filters.text & ~Filters.command, handle_trip_creation),
                CallbackQueryHandler(cancel, pattern="^cancel$"),  # Handle "Cancel" button clicks
                ],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
        # run_async=True
    )
dispatcher.add_handler(create_trip_handler)

trip_information_handler = ConversationHandler(
        entry_points=[CommandHandler("trip_info", trip_info_command)],
        states={
            states['HANDLE_TRIP_INFO_SELECTION']: [
                CallbackQueryHandler(handle_trip_info_selection),
                CallbackQueryHandler(cancel, pattern="^cancel$"),  # Handle "Cancel" button clicks
                ],
            states['GET_ITEM_INFO']: [
                CallbackQueryHandler(handle_get_item_info),
                CallbackQueryHandler(cancel, pattern="^cancel$"),  # Handle "Cancel" button clicks
                ],
            states['SHOW_ITEM_INFO']: [
                CallbackQueryHandler(handle_show_item_info),
                CallbackQueryHandler(cancel, pattern="^cancel$"),  # Handle "Cancel" button clicks
                ],
            # TODO: Future Tasks for Modify Trip, Delete Trip, Trip Summary ETC
            # states['MODIFY_TRIP_INFO']: [
            #     CallbackQueryHandler(handle_modify_trip_info),
            #     CallbackQueryHandler(cancel, pattern="^cancel$"),  # Handle "Cancel" button clicks
            #     ],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
        # run_async=True
    )
dispatcher.add_handler(trip_information_handler)

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