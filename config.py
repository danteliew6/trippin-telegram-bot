import os
import json
import logging
import gspread
from dotenv import load_dotenv
from telegram import Bot
import google
from googleapiclient.discovery import build
from google.cloud import firestore
from google.oauth2 import service_account
import google.generativeai as genai

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Sheets setup
SERVICE_ACCOUNT_FILE = os.environ.get("SERVICE_ACCOUNT_FILE", "SERVICE_ACCOUNT_FILE environment variable is not set.")
SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/cloud-platform"]
credentials, project_id = google.auth.default(scopes=SCOPES)
# credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# project_id="1"

gc = gspread.authorize(credentials)
drive_service = build('drive', 'v3', credentials=credentials)

# db = firestore.Client(credentials=credentials, project=project_id)
db = firestore.Client(credentials=credentials)

# Replace with your Google Sheet ID
FOLDER_ID = os.environ.get("FOLDER_ID", "FOLDER_ID environment variable is not set.")
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "SPREADSHEET_ID environment variable is not set.")
SHEET_NAME = os.environ.get("SHEET_NAME", "SHEET_NAME environment variable is not set.")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "GEMINI_API_KEY environment variable is not set.")
genai.configure(api_key=GEMINI_API_KEY)
sheet = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

bot = Bot(token=os.environ.get("TELEGRAM_TOKEN", "TELEGRAM_TOKEN environment variable is not set."))

