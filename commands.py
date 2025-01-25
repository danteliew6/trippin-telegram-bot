from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from config import db, TRAVEL_FILE_BUCKET_NAME, SELECTING_TRIP
from gcs_utils import check_folder_exists

# Telegram bot command handlers
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome! Please run the /upload_documents command and upload your travel document invoices or booking confirmation to track your purchases!")


def upload_documents(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_ref = db.collection("user_uploads").document(str(user_id))
    user_ref.set({"upload_mode": True})  # Set the user's state to "upload mode"
    update.message.reply_text("Please upload a PDF file for processing.")

def cancel_upload(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_ref = db.collection("user_uploads").document(str(user_id))
    user_ref.set({"upload_mode": False})  # Set the user's state to "not in upload mode"
    update.message.reply_text("Upload mode canceled. Type /upload_documents to start again.")


def select_trip(update: Update, context: CallbackContext) -> None:    
    user_id = update.message.from_user.id
    folder_prefix = f'{user_id}/{update.message.caption}'
    if check_folder_exists(TRAVEL_FILE_BUCKET_NAME,folder_prefix):
        user_ref = db.collection("user_uploads").document(str(user_id))
        user_ref.set({"selected_trip": update.message.caption})
        update.message.reply_text(f"Trip selected: {update.message.caption}")
        return ConversationHandler.END
    else:
        update.message.reply_text("Invalid trip selected, please create a trip before selecting.")
        return ConversationHandler.END

def select_trip_command(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    user_ref = db.collection("trips").document(user_id)

    # Fetch trips for the user
    user_doc = user_ref.get()
    if user_doc.exists:
        trips = user_doc.to_dict().get("trips", [])
        
        if not trips:
            update.message.reply_text("You don't have any trips yet! Create one using /create_trip.")
            return ConversationHandler.END

        # Display trips as a list
        trip_list = "\n".join([f"{i+1}. {trip}" for i, trip in enumerate(trips)])
        update.message.reply_text(
            f"Please select a trip by replying with the name:\n\n{trip_list}",
            reply_markup=ReplyKeyboardMarkup([[trip] for trip in trips], one_time_keyboard=True)
        )

        # Save trips to context for validation
        context.user_data["trips"] = trips
        return SELECTING_TRIP
    else:
        update.message.reply_text("You don't have any trips yet! Create one using /create_trip.")
        return ConversationHandler.END


def handle_trip_selection(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    selected_trip = update.message.text
    folder_prefix = f'{user_id}/{selected_trip}'
    if check_folder_exists(TRAVEL_FILE_BUCKET_NAME,folder_prefix):
        user_ref = db.collection("user_uploads").document(str(user_id))
        user_ref.update({"selected_trip": selected_trip})

        # Confirmation message
        update.message.reply_text(f"✅ You have selected '{selected_trip}' as your trip!")
        return ConversationHandler.END
    else:
        # Invalid selection
        update.message.reply_text(
            "❌ Invalid trip name. Please select a valid trip from the list."
        )
        return SELECTING_TRIP


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Conversation canceled.")
    return ConversationHandler.END