import os
from telegram.ext import CallbackContext, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from config import db, TRAVEL_FILE_BUCKET_NAME, states
from file_service import add_file_info_to_database, generate_summary_message, upload_to_gemini
from gcs_utils import check_folder_exists
from utils import generate_file_uuid, generate_trip_uuid
from db_functions import get_selected_trip, get_trips_ref, get_upload_mode, update_selected_trip, update_user_uploads, initialise_trips, initialise_trip_information, get_trip_uuid
from gcs_utils import upload_blob, delete_blob
    

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
                trips = trips_doc.to_dict()
                trip_buttons = [[InlineKeyboardButton(trip, callback_data=trip)] for trip in trips]
                trip_buttons.append([InlineKeyboardButton("Cancel", callback_data="cancel")])  # Cancel button

                query.edit_message_text(
                    "❌ Invalid trip name. Please select a valid trip from the list.",
                    reply_markup=InlineKeyboardMarkup(trip_buttons)
                )
                return states['SELECTING_TRIP']
        else:
            # Fallback for unexpected input (just in case)
            update.message.reply_text("Invalid input. Please try again.")
            return states['SELECTING_TRIP']
    except Exception as e:
        print(f'Error: {e}')
        # Invalid selection
        query.edit_message_text("❌ Error processing selection, please try again.")
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
        trips = trips_ref.get().to_dict()
        if not trips.get(trip_name, False):
            trips[trip_name] = {
                "uuid": trip_uuid,
                "num_people": int(trip_details[1])
            }
            trips_ref.update(trips)
            update_user_uploads(user_id, True)
            update_selected_trip(user_id, trip_name)
            initialise_trip_information(user_id, trip_name)

            print(f"Trip added for user {user_id}")
            update.message.reply_text(
                "Trip successfully created and this trip is now selected. \
                \n\n If you have multiple trips, you may use the /select_trip command to change trips."
            )
            return ConversationHandler.END
        else:
            update.message.reply_text(
                "This trip name is already used. Please try again with another trip name.\n\n Enter the required details with comma-separated delimiters (e.g. Australia,2).",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="cancel")]])
            )
            return states['CREATE_TRIP']
    except Exception as e:
        print(f'Error: {e}')
        # Invalid selection
        update.message.reply_text(
            "❌ Invalid trip details. Please enter the required details with comma-separated delimiters (e.g. Australia,2).",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="cancel")]])
        )
        return states['CREATE_TRIP']


# File handler to process uploaded files
def handle_file_upload(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)

    # Check if the user is in "upload mode"
    if not get_upload_mode(user_id):
        update.message.reply_text("Please use /upload_documents before uploading a file.")
        return
    
    file = update.message.document or update.message.photo[-1]

    # Get the file information
    file_id = file.file_id
    file_name = file.file_name if hasattr(file, "file_name") else ""
    file_extension = os.path.splitext(file_name)[1].lower()

    # Validate file type
    if file_extension not in [".pdf", ".png", ".jpeg", ".webp", ".heic", ".heif"]:
        update.message.reply_text("Unsupported file type! Please upload a PDF file or a valid image file.")
        return

    # Download the file locally
    # local_file_path = f"temp_{}"
    local_file_path = f"{generate_file_uuid()}{file_extension}"
    try:
        file_obj = context.bot.get_file(file_id)
        file_obj.download(local_file_path)

        selected_trip = get_selected_trip(user_id)
        trip_uuid = get_trip_uuid(user_id, selected_trip)
        
        destination_blob_name = f"{user_id}/{trip_uuid}/{local_file_path}"
        is_uploaded = upload_blob(TRAVEL_FILE_BUCKET_NAME, local_file_path, destination_blob_name)

        if not is_uploaded:
            raise Exception("Failed to upload file.")
        
        update.message.reply_text("File uploaded.")
        # Send the file to Gemini API
        extracted_data = upload_to_gemini(local_file_path, file_name)
        if not extracted_data:
            raise Exception("Failed to process the file. Please try again.")


        update.message.reply_text("File processed successfully! Adding data to the database...")
        # Append the extracted data to DB
        file_info = {
            "file_name": file_name,
            "file_extension": file_extension,
            "destination_blob_name": destination_blob_name
        }
        current_items = add_file_info_to_database(extracted_data, user_id, file_info)
        if not current_items:
            raise Exception("Failed to add extracted data to the database.")
        
        update.message.reply_text("Data successfully added to the database!")
        formatted_summary_message = generate_summary_message(user_id)
        update.message.reply_text(formatted_summary_message)

    except Exception as e:
        # Rollback if any step fails
        print(f"Error: {e}")
        update.message.reply_text(f"An error occurred: {e}. Rolling back...")
        
        # Attempt to delete the uploaded file from Cloud Storage if it exists
        try:
            delete_blob(TRAVEL_FILE_BUCKET_NAME, destination_blob_name)
            #TODO: REMOVE FIRESTORE DATA AS WELL
            print(f"Rolled back uploaded file: {destination_blob_name}")
        except Exception as delete_error:
            print(f"Failed to delete uploaded file during rollback: {delete_error}")

    finally:
        # Clean up the local file
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
            print(f"Cleaned up local file: {local_file_path}")