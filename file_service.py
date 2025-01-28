from config import db, genai
from gemini_protos_schema import extract_travel_document_data
from google.cloud import firestore
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
            ["Please extract the data from this document. \
             For any dates being extracted, ensure it follows the format DD-MM-YYYY. \
             For dates without year provided, use DD-MM only. \
             Purchase date should be blank if not specified.\
             For item_name field, return the following category values for the allocated category: \
             Hotels item name must be hotel name + check-in date + check-out date.\
             Rentals item name must be rental company name + rental pickup date.\
             Flights item name must be airline company name + departure airport + flight number.\
             Transport item name must be transport vehicle type + pickup location + datetime\
             ", uploaded_file],
            tool_config={'function_calling_config':'ANY'},
            generation_config=genai.GenerationConfig(temperature=0.1)
        )

        fc = response.candidates[0].content.parts[0].function_call
        return type(fc).to_dict(fc)
    except Exception as e:
        print(f"Error uploading to Gemini API: {e}")
        return None

def add_file_info_to_database(data: dict, user_id: str, file_info: dict) -> dict:
    try:
        trips_info_ref = get_trips_info_ref(user_id)
        selected_trip = get_selected_trip(user_id)
        common_data = data['args']['common_data']
        category_data = data['args']['category_data']
        combined_data = common_data | category_data | file_info
        transaction = db.transaction()
        category = data['args']['category']
        all_trip_info_data = trips_info_ref.get().to_dict()
        all_trip_info_data[selected_trip][category].append(combined_data)
        

        transaction.set(
            trips_info_ref,
            all_trip_info_data,
            merge=True
        )
        transaction.commit()
        return all_trip_info_data[selected_trip]
    except Exception as e:
        print(f"Error adding to database: {e}")
        return None

def generate_summary_message(user_id: str) -> str:
    trips_info_ref = get_trips_info_ref(user_id)
    selected_trip = get_selected_trip(user_id)
    current_items = trips_info_ref.get().to_dict()
    current_items = current_items.get(selected_trip)
    # Initialize variables for the formatted output and grand total
    formatted_output = 'Below is the updated summary of your trip items \n'
    grand_total = {}

    # Iterate over the categories in default_schema
    for category, items in current_items.items():
        # Add the category header
        formatted_output += f"{category}:\n"

        # Initialize category total
        category_total = {}

        # Iterate over items in the category
        for index, item in enumerate(items, start=1):
            # Format the item string
            item_string = f"  {index}. {item['item_name']} - {item['currency']} {item['price']}"
            formatted_output += item_string + "\n"

            # Add the price to the category total
            category_total[item['currency']] = category_total.get(item['currency'], 0) + item['price']
        
        if category_total:
            # Add category total to the output
            formatted_output += f"  Total for {category}: \n"
            for currency, total in category_total.items():
                formatted_output += f"  {currency} - {round(total,2)} \n"
                grand_total[currency] = grand_total.get(currency, 0) + total
            formatted_output += '\n'
        else:
            formatted_output += f"  No items added for this category yet. \n\n"


    # Add the grand total to the output
    formatted_output += "Grand Total: \n"
    for currency, total in grand_total.items():
        formatted_output += f"  {currency} - {round(total,2)} \n"

    return formatted_output
