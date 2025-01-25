from google.cloud import storage_control_v2, storage


def create_folder(bucket_name: str, folder_name: str) -> None:
    # The ID of your GCS bucket
    # bucket_name = "your-unique-bucket-name"

    # The name of the folder to be created
    # folder_name = "folder-name"

    storage_control_client = storage_control_v2.StorageControlClient()
    # The storage bucket path uses the global access pattern, in which the "_"
    # denotes this bucket exists in the global namespace.
    project_path = storage_control_client.common_project_path("_")
    bucket_path = f"{project_path}/buckets/{bucket_name}"

    request = storage_control_v2.CreateFolderRequest(
        parent=bucket_path,
        folder_id=folder_name,
    )
    response = storage_control_client.create_folder(request=request)

    print(f"Created folder: {response.name}")

def check_folder_exists(bucket_name: str, folder_name: str) -> bool:
    storage_client = storage.Client()  # Ensure credentials are set up properly
    bucket = storage_client.bucket(bucket_name)
    
    # Append a trailing slash to check for folders
    folder_prefix = f"{folder_name}/"

    # List blobs with the specified prefix
    blobs = bucket.list_blobs(prefix=folder_prefix, max_results=1)  # Check for existence

    # If there's at least one blob with the prefix, the folder exists
    return True if blobs else False


def list_folders(bucket_name: str) -> None:
    # The ID of your GCS bucket
    # bucket_name = "your-unique-bucket-name"

    storage_control_client = storage_control_v2.StorageControlClient()
    # The storage bucket path uses the global access pattern, in which the "_"
    # denotes this bucket exists in the global namespace.
    project_path = storage_control_client.common_project_path("_")
    bucket_path = f"{project_path}/buckets/{bucket_name}"

    request = storage_control_v2.ListFoldersRequest(
        parent=bucket_path,
    )

    page_result = storage_control_client.list_folders(request=request)
    for folder in page_result:
        print(folder)

    print(f"Listed folders in bucket {bucket_name}")

def delete_folder(bucket_name: str, folder_name: str) -> None:
    # The ID of your GCS bucket
    # bucket_name = "your-unique-bucket-name"

    # The name of the folder to be deleted
    # folder_name = "folder-name"

    storage_control_client = storage_control_v2.StorageControlClient()
    # The storage bucket path uses the global access pattern, in which the "_"
    # denotes this bucket exists in the global namespace.
    folder_path = storage_control_client.folder_path(
        project="_", bucket=bucket_name, folder=folder_name
    )

    request = storage_control_v2.DeleteFolderRequest(
        name=folder_path,
    )
    storage_control_client.delete_folder(request=request)

    print(f"Deleted folder {folder_name}")

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    try:
        """Uploads a file to the bucket."""
        # The ID of your GCS bucket
        # bucket_name = "your-bucket-name"
        # The path to your file to upload
        # source_file_name = "local/path/to/file"
        # The ID of your GCS object
        # destination_blob_name = "storage-object-name"

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        # Optional: set a generation-match precondition to avoid potential race conditions
        # and data corruptions. The request to upload is aborted if the object's
        # generation number does not match your precondition. For a destination
        # object that does not yet exist, set the if_generation_match precondition to 0.
        # If the destination object already exists in your bucket, set instead a
        # generation-match precondition using its generation number.
        generation_match_precondition = 0

        blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)

        print(
            f"File {source_file_name} uploaded to {destination_blob_name}."
        )
        return True
    except Exception as e:
        print(
            f"Error uploading file {source_file_name}: {e}"
        )
        return False