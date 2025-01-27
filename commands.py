from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler
from config import db, states
from gcs_utils import check_folder_exists
from db_functions import update_user_uploads, get_trips_ref, user_initialised
# Telegram bot command handlers
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome! Please run the /create_trip command to begin your journey in tracking your itinerary!")
    return ConversationHandler.END


def upload_documents(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    if not user_initialised(user_id):
        update.message.reply_text("Error, please create and select your trip before enabling upload")
        return ConversationHandler.END


    update_user_uploads(user_id, True)
    update.message.reply_text("Upload has been enabled! you can upload your travel document invoices or booking confirmation in PDF or image files to track your purchases.")
    return ConversationHandler.END

def cancel_upload(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    if not user_initialised(user_id):
        update.message.reply_text("Error, unable to cancel as you have not created or selected your trip")
        return ConversationHandler.END

    update_user_uploads(user_id, False)
    update.message.reply_text("Upload mode canceled. Type /upload_documents to start again.")
    return ConversationHandler.END


def select_trip_command(update: Update, context: CallbackContext):
    print('Selecting trip....')
    user_id = str(update.message.from_user.id)
    trips_ref = get_trips_ref(user_id)

    # Fetch trips for the user
    trips_doc = trips_ref.get()
    if trips_doc.exists:
        trips = trips_doc.to_dict().get("trips", {})
        # TODO: MODIFY THIS TO DICT
        if not trips:
            update.message.reply_text("You don't have any trips yet! Create one using /create_trip.")
            return ConversationHandler.END

        # Display trips as a list
        trip_list = "\n".join([f"{i+1}. {key}: {value['num_people']} Pax" for i, (key, value) in enumerate(trips.items())])
        trip_buttons = [[InlineKeyboardButton(trip, callback_data=trip)] for trip in trips]
        trip_buttons.append([InlineKeyboardButton("Cancel", callback_data="cancel")])  # Cancel button
        update.message.reply_text(
            f"Please select a trip:\n\n{trip_list}",
            reply_markup=InlineKeyboardMarkup(trip_buttons, one_time_keyboard=True)
        )

        # Save trips to context for validation
        context.user_data["trips"] = trips
        return states['SELECTING_TRIP']
    else:
        update.message.reply_text("You don't have any trips yet! Create one using /create_trip.")
        
        return cancel(update, context)


def cancel(update: Update, context: CallbackContext):
    """Handle cancel action triggered by the cancel button."""
    query = update.callback_query
    query.answer()  # Acknowledge the callback
    query.edit_message_text("❌ You have canceled the action.")
    return ConversationHandler.END

def create_trip_command(update: Update, context: CallbackContext):
    print('Creating trip....')
    update.message.reply_text("To start creating, we will require some details from you:\
                              \n\n 1. Name/Title of the trip\n 2. Number of people going on the trip \
                              \n\n Please enter the details separated by a comma (e.g. Australia,2)",\
                            reply_markup=InlineKeyboardMarkup([InlineKeyboardButton("Cancel", callback_data="cancel")], one_time_keyboard=True))
    return states['CREATE_TRIP']