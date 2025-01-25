from telegram import Update
from telegram.ext import CallbackContext
from config import db


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