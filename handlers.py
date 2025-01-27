from telegram.ext import CallbackContext, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup
from config import db, TRAVEL_FILE_BUCKET_NAME, states
from gcs_utils import check_folder_exists
from utils import generate_trip_uuid
from db_functions import get_trips_ref, update_selected_trip, update_user_uploads, initialise_trips, initialise_trip_information, get_trip_uuid
    

def handle_trip_selection(update: Update, context: CallbackContext):
    try:
        query = update.callback_query  # Inline button interactions
        if query:
            user_id = str(query.from_user.id)
            query.answer()  # Acknowledge the callback
            selected_trip = query.data
            folder_prefix = f'{user_id}/{get_trip_uuid(user_id, selected_trip)}'
            if check_folder_exists(TRAVEL_FILE_BUCKET_NAME,folder_prefix):
                user_ref = db.collection("user_uploads").document(str(user_id))
                user_ref.update({"selected_trip": selected_trip})

                # Confirmation message
                query.edit_message_text(f"✅ You have selected '{selected_trip}' as your trip!")
                return ConversationHandler.END
            else:
                # Invalid selection
                trips_ref = get_trips_ref(user_id)
                trips_doc = trips_ref.get()
                trips = trips_doc.to_dict().get("trips", {})
                trip_buttons = [[InlineKeyboardButton(trip, callback_data=trip)] for trip in trips]
                trip_buttons.append([InlineKeyboardButton("Cancel", callback_data="cancel")])  # Cancel button

                query.edit_message_text(\
                    "❌ Invalid trip name. Please select a valid trip from the list.",\
                    reply_markup=InlineKeyboardMarkup(trip_buttons)\
                )
                return states['SELECTING_TRIP']
        else:
            # Fallback for unexpected input (just in case)
            update.message.reply_text("Invalid input. Please try again.")
            return states['SELECTING_TRIP']
    except Exception as e:
        print(f'Error: {e}')
        # Invalid selection
        update.message.reply_text("❌ Error processing selection, please try again.")
        return ConversationHandler.END

    
def handle_trip_creation(update: Update, context: CallbackContext):
    try:
        user_id = str(update.message.from_user.id)
        trip_details = update.message.text.split(',')
        trip_name = trip_details[0]
        trip_uuid = generate_trip_uuid(trip_name)
        trips_ref = get_trips_ref(user_id)
        
        initialise_trips(user_id)
        # initialise_gcs_folder(user_id, trip_uuid)
        trips = trips_ref.get().to_dict().get('trips')
        if not trips.get(trip_name, False):
            trips[trip_name] = {
                "uuid": trip_uuid,
                "num_people": int(trip_details[1])
            }
            trips_ref.update({"trips": trips})
            update_user_uploads(user_id, True)
            update_selected_trip(user_id, trip_name)
            initialise_trip_information(user_id)

            print(f"Trip added for user {user_id}")
            update.message.reply_text(\
                "Trip successfully created and this trip is now selected. \
                \n\n If you have multiple trips, you may use the /select_trip command to change trips."\
            )
            return ConversationHandler.END
        else:
            update.message.reply_text(\
                "This trip name is already used. Please try again with another trip name.\n\n Enter the required details with comma-separated delimiters (e.g. Australia,2).",\
                reply_markup=InlineKeyboardMarkup([InlineKeyboardButton("Cancel", callback_data="cancel")], one_time_keyboard=True)\
            )
            return states['CREATE_TRIP']
    except Exception as e:
        print(f'Error: {e}')
        # Invalid selection
        update.message.reply_text(\
            "❌ Invalid trip details. Please enter the required details with comma-separated delimiters (e.g. Australia,2).",\
            reply_markup=InlineKeyboardMarkup([InlineKeyboardButton("Cancel", callback_data="cancel")], one_time_keyboard=True)\
        )
        return states['CREATE_TRIP']
