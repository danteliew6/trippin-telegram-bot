from vertexai.generative_models import FunctionDeclaration

# Define the schema for 'common_data'
common_data = {
    "type": "object",
    "properties": {
        "item_name": {"type": "string", "description": "The name of the item. For these categories, follow the pattern specified: Hotel items must be hotel name, Flights must be airline name and flight number, Transport must be company and type, Rentals must be the rental company name and pick-up location."},
        "price": {"type": "number", "description": "The price of the item."},
        "currency": {"type": "string", "description": "The currency used for this purchase. If not specified, should be defaulted to SGD."},
        "date_of_purchase": {"type": "string", "description": "The date of purchase. If not specified, use the current date."},
        "instructions": {"type": "string", "description": "Additional instructions or notes."},
    },
    "required": ["item_name", "price", "date_of_purchase"]
}

# Define the schema for 'category'
category = {
    "type": "string",
    "enum": ["Hotels", "Flights", "Transport", "Rentals", "Activities", "Insurance", "Miscellaneous"],
    "description": "The category of the travel document."
}

# Define the schema for 'category_data'
category_data = {
    "type": "object",
    "properties": {
        "check_in_date": {"type": "string", "description": "Check-in date for hotels."},
        "check_in_timing": {"type": "string", "description": "Stipulated check-in timing for hotels."},
        "check_out_date": {"type": "string", "description": "Check-out date for hotels."},
        "check_out_timing": {"type": "string", "description": "Stipulated check-out timing for hotels."},
        "location": {"type": "string", "description": "Address of the hotel or activity."},
        "room_type": {"type": "string", "description": "Type of room for hotels."},
        
        "departure_datetime": {"type": "string", "description": "Flight departure date and time."},
        "arrival_datetime": {"type": "string", "description": "Flight arrival date and time."},
        "departure_airport": {"type": "string", "description": "Departure airport and boarding terminal."},
        "arrival_airport": {"type": "string", "description": "Arrival airport and boarding terminal."},
        "airline": {"type": "string", "description": "Airline name."},
        "flight_number": {"type": "string", "description": "Flight number."},
        
        "pickup_location": {"type": "string", "description": "Transport pickup location."},
        "dropoff_location": {"type": "string", "description": "Transport drop-off location."},
        "date_time": {"type": "string", "description": "Transport date and time."},
        "transport_vehicle_type": {"type": "string", "description": "Type of vehicle for transport."},
        
        "rental_start_date": {"type": "string", "description": "Rental start date."},
        "rental_end_date": {"type": "string", "description": "Rental end date."},
        "rental_company": {"type": "string", "description": "Rental company name."},
        "rental_vehicle_type": {"type": "string", "description": "Type of rented vehicle."},
        "pickup_instructions": {"type": "string", "description": "Instructions and steps to pick up the car, if any."},
        "dropoff_instructions": {"type": "string", "description": "Instructions and steps in returning the car, if any."},
        
        "activity_date": {"type": "string", "description": "Date of the activity."},
        "activity_type": {"type": "string", "description": "Type of activity."},
        "provider": {"type": "string", "description": "Provider of the activity."},
        "description": {"type": "string", "description": "Description of the activity."},
        
        "policy_number": {"type": "string", "description": "Insurance policy number."},
        "coverage_start_date": {"type": "string", "description": "Start date of insurance coverage."},
        "coverage_end_date": {"type": "string", "description": "End date of insurance coverage."},
        "insured_amount": {"type": "number", "description": "Insured amount."},
        
        "subcategory": {"type": "string", "description": "Subcategory for the miscellaneous item, if needed."},
    }
}

# Define the FunctionDeclaration for 'extract_travel_document_data'
extract_travel_document_data = FunctionDeclaration(
    name="extract_travel_document_data",
    description="Extracts structured data from travel-related documents.",
    parameters={
        "type": "object",
        "properties": {
            "common_data": common_data,
            "category": category,
            "category_data": category_data
        },
        "required": ["common_data", "category"]
    }
)