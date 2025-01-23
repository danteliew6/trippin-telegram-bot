import os
import json
import logging
import gspread
from dotenv import load_dotenv
from telegram import Bot
import google

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Sheets setup
SERVICE_ACCOUNT_FILE = os.environ.get("SERVICE_ACCOUNT_FILE", "SERVICE_ACCOUNT_FILE environment variable is not set.")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

credentials = google.auth.default(scopes=SCOPES)
gc = gspread.authorize(credentials)

# Replace with your Google Sheet ID
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "SPREADSHEET_ID environment variable is not set.")
SHEET_NAME = os.environ.get("SHEET_NAME", "SHEET_NAME environment variable is not set.")
sheet = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

bot = Bot(token=os.environ.get("TELEGRAM_TOKEN", "TELEGRAM_TOKEN environment variable is not set."))