from config import db

def update_user_uploads(user_id: str, upload_mode: bool):
    user_ref = db.collection("user_uploads").document(user_id)
    user_ref.set({"upload_mode": upload_mode}, merge=True) 

def update_selected_trip(user_id: str, selected_trip: str):
    user_ref = db.collection("user_uploads").document(user_id)
    user_ref.set({"selected_trip": selected_trip}, merge=True) 

def get_trips_ref(user_id: str):
    return db.collection("trips").document(user_id)

def get_trips_info_ref(user_id: str):
    return db.collection("trip_information").document(user_id)

def get_user_uploads_ref(user_id: str):
    return db.collection("user_uploads").document(user_id)

def get_selected_trip(user_id):
    uploads_ref = db.collection("user_uploads").document(user_id)
    doc = uploads_ref.get().to_dict()
    return doc.get("selected_trip", None)

def get_upload_mode(user_id):
    uploads_ref = db.collection("user_uploads").document(user_id)
    doc = uploads_ref.get().to_dict()
    return doc.get("upload_mode", False)

def get_trip_uuid(user_id, selected_trip):
    trips_ref = db.collection("trips").document(user_id)
    doc = trips_ref.get().to_dict()
    return doc[selected_trip]['uuid']

def initialise_trips(user_id):
    trips_ref = db.collection("trips").document(user_id)
    doc = trips_ref.get()
    if not doc.exists:
        trips_ref.set({})

def initialise_trip_information(user_id, trip_name):
    trip_info_ref = db.collection("trip_information").document(user_id)
    default_schema = {
        trip_name: {
            "Hotels": [],
            "Flights": [],
            "Transport": [],
            "Rentals": [],
            "Activities": [],
            "Insurance": [],
            "Miscellaneous": [],
        }
    }

    # Create the document with the default schema
    trip_info_ref.set(default_schema, merge=True)


def user_initialised(user_id: str):
    user_ref = db.collection("user_uploads").document(user_id)
    doc = user_ref.get()
    return  doc.exists and doc.to_dict().get('upload_mode', False) and doc.to_dict().get('selected_trip', False)