from telegram import Update
from telegram.ext import CallbackContext
import os
from config import FOLDER_ID, drive_service, db, genai, TRAVEL_FILE_BUCKET_NAME
from googleapiclient.http import MediaFileUpload
from gemini_protos_schema import extract_travel_document_data
from utils import generate_file_uuid
from google.cloud import firestore
from gcs_utils import upload_blob
from db_functions import get_trips_info_ref, get_selected_trip, get_upload_mode, get_trip_uuid

# Upload file to Google Drive
# def upload_to_google_drive(file_path: str, file_name: str) -> str:
#     file_metadata = {"name": file_name, "parents": [FOLDER_ID]}
#     media = MediaFileUpload(file_path, resumable=True)

#     try:
#         # Check if a file with the same name exists in the target folder
#         query = f"'{FOLDER_ID}' in parents and name = '{file_name}' and trashed = false"
#         response = drive_service.files().list(q=query, fields="files(id, name)").execute()
#         files = response.get("files", [])

#         # If a file with the same name exists, delete it
#         if files:
#             for file in files:
#                 drive_service.files().delete(fileId=file["id"]).execute()
#                 print(f"Deleted existing file: {file['name']} with ID: {file['id']}")

#         # Upload the new file
#         file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
#         print(f"Uploaded file: {file_name} with ID: {file.get('id')}")
#         return file.get("id")
#     except Exception as e:
#         print(f"Google Drive Upload Error: {e}")
#         return None

# Upload file to Gemini API
def upload_to_gemini(file_path: str, file_name: str) -> dict:
    try:
        mime_type = file_name.split('.')[-1].lower()
        if mime_type == 'pdf':
            uploaded_file = genai.upload_file(path=file_path, display_name=file_name, mime_type="application/pdf")
        else: 
            uploaded_file = genai.upload_file(path=file_path, display_name=file_name, mime_type=f"image/{mime_type}")

        model = genai.GenerativeModel("gemini-1.5-flash", tools=[extract_travel_document_data])
        response = model.generate_content(
            ["Please extract the data from this document. For any dates being extracted, ensure it follows the format DD-MM-YYYY. For dates without year provided, use DD-MM only. Purchase date should be blank if not specified", uploaded_file],
            tool_config={'function_calling_config':'ANY'}
        )

        fc = response.candidates[0].content.parts[0].function_call
        return type(fc).to_dict(fc)
    except Exception as e:
        print(f"Error uploading to Gemini API: {e}")
        return None

def add_to_database(data: dict, user_id: str) -> dict:
    try:
        trips_info_ref = get_trips_info_ref(user_id)
        selected_trip = get_selected_trip(user_id)
        # if not doc.to_dict().get(selected_trip, False):
        #     default_schema = {
        #         selected_trip: {
        #             "Hotels": [],
        #             "Flights": [],
        #             "Transport": [],
        #             "Rentals": [],
        #             "Activities": [],
        #             "Insurance": [],
        #             "Miscellaneous": [],
        #         }
        #     }

        #     # Create the document with the default schema
        #     trips_info_ref.set(default_schema)
        #     print(f"Default schema created for user {user_id}.")
        # else:
        #     print(f"Document for user {user_id} already exists.")

        common_data = data['args']['common_data']
        category_data = data['args']['category_data']
        combined_data = common_data | category_data
        trips_info_ref.update({selected_trip: {data['args']['category']: firestore.ArrayUnion([combined_data])}})
        return trips_info_ref.get().to_dict()
    except Exception as e:
        print(f"Error adding to database: {e}")
        return None

def generate_summary_message(user_id: str) -> str:
    current_items = db.collection("trip_information").document(user_id).get().to_dict()
    # Initialize variables for the formatted output and grand total
    formatted_output = 'Below is the updated summary of your trip items \n'
    grand_total = 0

    # Iterate over the categories in default_schema
    for category, items in current_items.items():
        # Add the category header
        formatted_output += f"{category}:\n"

        # Initialize category total
        category_total = 0

        # Iterate over items in the category
        for index, item in enumerate(items, start=1):
            # Format the item string
            item_string = f"  {index}. {item['item_name']} - {item['price']}"
            formatted_output += item_string + "\n"

            # Add the price to the category total
            category_total += item['price']

        # Add category total to the output
        formatted_output += f"  Total for {category}: {category_total}\n\n"

        # Add category total to the grand total
        grand_total += category_total

    # Add the grand total to the output
    formatted_output += f"Grand Total: {grand_total}"

    return formatted_output


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
    file_obj = context.bot.get_file(file_id)
    file_obj.download(local_file_path)

    selected_trip = get_selected_trip(user_id)
    trip_uuid = get_trip_uuid(user_id, selected_trip)
    
    destination_blob_name = f"{user_id}/{trip_uuid}/{local_file_path}"
    is_uploaded = upload_blob(TRAVEL_FILE_BUCKET_NAME, file_name, destination_blob_name)

    if not is_uploaded:
        update.message.reply_text("Failed to upload file to Google Drive.")
        return
    else:
        update.message.reply_text("File uploaded to Google Drive.")

    # Send the file to Gemini API
    extracted_data = upload_to_gemini(local_file_path, file_name)
    os.remove(local_file_path)  # Clean up local file

    if extracted_data:
        update.message.reply_text("File processed successfully! Adding data to the database...")
        # Append the extracted data to Google Sheets
        current_items = add_to_database(extracted_data, str(user_id))
        if current_items:
            update.message.reply_text("Data successfully added to the database!")
            formatted_summary_message = generate_summary_message(str(user_id))
            update.message.reply_text(formatted_summary_message)
        else:
            update.message.reply_text("Failed to upload data to database. Please try again.")
    else:
        update.message.reply_text("Failed to process the file. Please try again.")