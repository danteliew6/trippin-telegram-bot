# from telegram import Update
# from telegram.ext import CallbackContext
# from config import sheet

# def add_purchase(update: Update, context: CallbackContext) -> None:
#     try:
#         # Parse user message
#         message = update.message.text
#         item, cost, date = [x.strip() for x in message.split(",")]

#         # Append to Google Sheet
#         sheet.append_row([item, cost, date])

#         update.message.reply_text(f"Added: {item} (${cost}) on {date}")
#     except Exception as e:
#         print(f"Error: {e}")
#         update.message.reply_text("Invalid format. Please send details as: Item, Cost, Date")