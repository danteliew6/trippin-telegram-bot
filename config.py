import os
import logging
import gspread
from dotenv import load_dotenv
from telegram import Bot
import google
from googleapiclient.discovery import build
from google.cloud import firestore
import vertexai

load_dotenv()
states = {
    "CREATE_TRIP": "1",
    "GATHER_TRIP_INFO": "2",
    "SELECTING_TRIP": "3",
    "HANDLE_TRIP_INFO_SELECTION": "4",
    "GET_ITEM_INFO": "5",
    "MODIFY_ITEM_INFO": "6",
    "SHOW_ITEM_INFO": "7",
}

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Sheets setup
SERVICE_ACCOUNT_FILE = os.environ.get("SERVICE_ACCOUNT_FILE", "SERVICE_ACCOUNT_FILE environment variable is not set.")
SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/cloud-platform"]
credentials, project_id = google.auth.default(scopes=SCOPES)

gc = gspread.authorize(credentials)
drive_service = build('drive', 'v3', credentials=credentials)

db = firestore.Client(credentials=credentials, project=project_id)
TRAVEL_FILE_BUCKET_NAME = os.environ.get("TRAVEL_FILE_BUCKET_NAME", "TRAVEL_FILE_BUCKET_NAME environment variable is not set.")


# Replace with your Google Sheet ID
FOLDER_ID = os.environ.get("FOLDER_ID", "FOLDER_ID environment variable is not set.")
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "SPREADSHEET_ID environment variable is not set.")
SHEET_NAME = os.environ.get("SHEET_NAME", "SHEET_NAME environment variable is not set.")
vertexai.init(project=project_id, service_account=os.environ.get("SERVICE_ACCOUNT", "SERVICE_ACCOUNT environment variable is not set."))


# sheet = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

bot = Bot(token=os.environ.get("TELEGRAM_TOKEN", "TELEGRAM_TOKEN environment variable is not set."))

