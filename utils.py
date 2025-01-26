import uuid

def generate_trip_uuid(trip_name: str):
    trip_namespace = uuid.NAMESPACE_DNS
    trip_uuid = uuid.uuid5(trip_namespace, trip_name).hex[:8]

    return trip_uuid

def generate_file_uuid():
    return uuid.uuid4().hex[:8]