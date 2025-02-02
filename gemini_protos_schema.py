import google.generativeai as genai
import textwrap
from vertexai.generative_models import FunctionDeclaration

# Define the schema for 'common_data'
common_data = genai.protos.Schema(
    type=genai.protos.Type.OBJECT,
    properties={
        'item_name': genai.protos.Schema(type=genai.protos.Type.STRING, description="The name of the item. For these categories, follow the pattern specified: Hotel items must be hotel name, Flights must be airline name and flight number, Transport must be company and type, Rentals must be the rental company name and pick up location)"),
        'price': genai.protos.Schema(type=genai.protos.Type.NUMBER, description="The price of the item."),
        'currency': genai.protos.Schema(type=genai.protos.Type.STRING, description="The currency used for this purchase. If not specified, should be defaulted to SGD"),
        'date_of_purchase': genai.protos.Schema(type=genai.protos.Type.STRING, description="The date of purchase. If not specified, use current date"),
        'instructions': genai.protos.Schema(type=genai.protos.Type.STRING, description="Additional instructions or notes."),
    },
    required=["item_name", "price", "date_of_purchase"]
)

# Define the schema for 'category'
category = genai.protos.Schema(
    type=genai.protos.Type.STRING,
    enum=["Hotels", "Flights", "Transport", "Rentals", "Activities", "Insurance", "Miscellaneous"],
    description="The category of the travel document."
)

# Define the schema for 'category_data'
category_data = genai.protos.Schema(
    type=genai.protos.Type.OBJECT,
    properties={
        # Hotels
        "check_in_date": genai.protos.Schema(type=genai.protos.Type.STRING, description="Check-in date for hotels."),
        "check_in_timing": genai.protos.Schema(type=genai.protos.Type.STRING, description="Stipulated Check-in timing for hotels"),
        "check_out_date": genai.protos.Schema(type=genai.protos.Type.STRING, description="Check-out date for hotels."),
        "check_out_timing": genai.protos.Schema(type=genai.protos.Type.STRING, description="Stipulated Check-out timing for hotels."),
        "location": genai.protos.Schema(type=genai.protos.Type.STRING, description="Address of the hotel or activity."),
        "room_type": genai.protos.Schema(type=genai.protos.Type.STRING, description="Type of room for hotels."),

        # Flights
        "departure_datetime": genai.protos.Schema(type=genai.protos.Type.STRING, description="Flight departure date and time."),
        "arrival_datetime": genai.protos.Schema(type=genai.protos.Type.STRING, description="Flight arrival date and time."),
        "departure_airport": genai.protos.Schema(type=genai.protos.Type.STRING, description="Departure airport and boarding terminal."),
        "arrival_airport": genai.protos.Schema(type=genai.protos.Type.STRING, description="Arrival airport and boarding terminal."),
        "airline": genai.protos.Schema(type=genai.protos.Type.STRING, description="Airline name."),
        "flight_number": genai.protos.Schema(type=genai.protos.Type.STRING, description="Flight number."),

        # Transport
        "pickup_location": genai.protos.Schema(type=genai.protos.Type.STRING, description="Transport pickup location."),
        "dropoff_location": genai.protos.Schema(type=genai.protos.Type.STRING, description="Transport drop-off location."),
        "date_time": genai.protos.Schema(type=genai.protos.Type.STRING, description="Transport date and time."),
        "transport_vehicle_type": genai.protos.Schema(type=genai.protos.Type.STRING, description="Type of vehicle for transport."),

        # Rentals
        "rental_start_date": genai.protos.Schema(type=genai.protos.Type.STRING, description="Rental start date."),
        "rental_end_date": genai.protos.Schema(type=genai.protos.Type.STRING, description="Rental end date."),
        "rental_company": genai.protos.Schema(type=genai.protos.Type.STRING, description="Rental company name."),
        "rental_vehicle_type": genai.protos.Schema(type=genai.protos.Type.STRING, description="Type of rented vehicle."),
        "pickup_location": genai.protos.Schema(type=genai.protos.Type.STRING, description="Specified address to pick up the car."),
        "dropoff_location": genai.protos.Schema(type=genai.protos.Type.STRING, description="Specified address to return the car after rental."),
        "pickup_instructions": genai.protos.Schema(type=genai.protos.Type.STRING, description="Instructions and steps to pick up the car, if any."),
        "dropoff_instructions": genai.protos.Schema(type=genai.protos.Type.STRING, description="Instructions and steps in returning the car, if any."),
        

        # Activities
        "activity_date": genai.protos.Schema(type=genai.protos.Type.STRING, description="Date of the activity."),
        "activity_type": genai.protos.Schema(type=genai.protos.Type.STRING, description="Type of activity."),
        "provider": genai.protos.Schema(type=genai.protos.Type.STRING, description="Provider of the activity."),
        "description": genai.protos.Schema(type=genai.protos.Type.STRING, description="Description of the activity."),

        # Insurance
        "policy_number": genai.protos.Schema(type=genai.protos.Type.STRING, description="Insurance policy number."),
        "coverage_start_date": genai.protos.Schema(type=genai.protos.Type.STRING, description="Start date of insurance coverage."),
        "coverage_end_date": genai.protos.Schema(type=genai.protos.Type.STRING, description="End date of insurance coverage."),
        "insured_amount": genai.protos.Schema(type=genai.protos.Type.NUMBER, description="Insured amount."),

        # Miscellaneous
        "description": genai.protos.Schema(type=genai.protos.Type.STRING, description="Description of the miscellaneous item."),
        "date_time": genai.protos.Schema(type=genai.protos.Type.STRING, description="Date and time for the item."),
        "subcategory": genai.protos.Schema(type=genai.protos.Type.STRING, description="Subcategory for the miscellaneous item, if needed.")
    }
)

# Define the FunctionDeclaration for 'extract_travel_document_data'
extract_travel_document_data = FunctionDeclaration(
    name="extract_travel_document_data",
    description=textwrap.dedent("""\
        Extracts structured data from travel-related documents.
        """),
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            'common_data': common_data,
            'category': category,
            'category_data': category_data
        },
        required=['common_data', 'category']
    )
)