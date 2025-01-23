from telegram import Update
from telegram.ext import CallbackContext
import os
from config import FOLDER_ID, drive_service, db
from googleapiclient.http import MediaFileUpload


# File handler to process uploaded files
def handle_file_upload(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_ref = db.collection("user_uploads").document(str(user_id))
    user_doc = user_ref.get()

    # Check if the user is in "upload mode"
    if not user_doc.exists or not user_doc.to_dict().get("upload_mode", False):
        update.message.reply_text("Please use /upload_documents before uploading a file.")
        return
    
    file = update.message.document or update.message.photo[-1]

    # Get the file information
    file_id = file.file_id
    file_name = file.file_name if hasattr(file, "file_name") else "image.jpg"
    file_extension = os.path.splitext(file_name)[1].lower()

    # Validate file type
    if file_extension not in [".pdf", ".png", ".jpg", ".jpeg"]:
        update.message.reply_text("Unsupported file type! Please upload a PDF or image file.")
        return

    # Download the file locally
    local_file_path = f"temp_{file_name}"
    file_obj = context.bot.get_file(file_id)
    file_obj.download(local_file_path)

    # Upload the file to Google Drive
    drive_file_id = upload_to_google_drive(local_file_path, file_name)
    if not drive_file_id:
        update.message.reply_text("Failed to upload file to Google Drive.")
        return
    else:
        update.message.reply_text("File uploaded to Google Drive.")

    # Send the file to Gemini API
    # response = upload_to_gemini(local_file_path)
    # os.remove(local_file_path)  # Clean up local file

    # if response:
    #     update.message.reply_text("File processed successfully! Adding data to the spreadsheet...")
        # # Append the extracted data to Google Sheets
        # append_to_google_sheets(response)
        # update.message.reply_text("Data successfully added to the spreadsheet!")
    # else:
    #     update.message.reply_text("Failed to process the file. Please try again.")

# Upload file to Google Drive
def upload_to_google_drive(file_path: str, file_name: str) -> str:
    file_metadata = {"name": file_name, "parents": [FOLDER_ID]}
    media = MediaFileUpload(file_path, resumable=True)
    try:
        file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        return file.get("id")
    except Exception as e:
        print(f"Google Drive Upload Error: {e}")
        return None

# # Upload file to Gemini API
# def upload_to_gemini(file_path: str) -> dict:
#     with open(file_path, "rb") as file:
#         files = {"file": file}
#         headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
#         try:
#             response = requests.post(GEMINI_API_URL, files=files, headers=headers)
#             if response.status_code == 200:
#                 return response.json().get("data", "No data extracted.")
#             else:
#                 print(f"Gemini API Error: {response.status_code} - {response.text}")
#                 return None
#         except Exception as e:
#             print(f"Error uploading to Gemini API: {e}")
#             return None

# # Append data to Google Sheets
# def append_to_google_sheets(data: dict) -> None:
#     # Prepare data for insertion
#     rows = [[key, value] for key, value in data.items()]

#     # Append the data
#     body = {"values": rows}
#     try:
#         sheets_service.spreadsheets().values().append(
#             spreadsheetId=GOOGLE_SHEET_ID,
#             range="Sheet1",  # Adjust the range as needed
#             valueInputOption="RAW",
#             body=body,
#         ).execute()
#     except Exception as e:
#         print(f"Google Sheets Append Error: {e}")