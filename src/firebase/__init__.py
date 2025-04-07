import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request


def get_firestore_access_token(service_account_path: str) -> str:
    """
    Generates an access token for Firestore REST API using the service account.

    Args:
        service_account_path (str): Path to your service account key JSON file.

    Returns:
        str: Access token string.
    """
    credentials = service_account.Credentials.from_service_account_file(
        service_account_path, scopes=["https://www.googleapis.com/auth/datastore"]
    )
    credentials.refresh(Request())
    return credentials.token


def insert_document_firestore_rest(
    access_token: str,
    collection: str,
    document_data: dict,
    project_id: str = "english-news-article",
) -> str:
    """
    Inserts a document into Firestore via the REST API.

    Args:
        access_token (str): OAuth2 access token for Firestore.
        project_id (str): Your Firebase/GCP project ID.
        collection (str): Firestore collection name.
        document_data (dict): Document data in Python dict format.

    Returns:
        str: Response from Firestore (usually JSON string with document name or error).
    """

    def to_firestore_fields(data: dict) -> dict:
        def wrap_value(value):
            if isinstance(value, str):
                return {"stringValue": value}
            elif isinstance(value, bool):
                return {"booleanValue": value}
            elif isinstance(value, int):
                return {"integerValue": str(value)}
            elif isinstance(value, float):
                return {"doubleValue": value}
            elif isinstance(value, list):
                return {"arrayValue": {"values": [wrap_value(v) for v in value]}}
            elif isinstance(value, dict):
                return {"mapValue": {"fields": to_firestore_fields(value)}}
            elif value is None:
                return {"nullValue": None}
            else:
                raise ValueError(f"Unsupported type for value: {value} ({type(value)})")

        return {key: wrap_value(val) for key, val in data.items()}

    firestore_fields = to_firestore_fields(document_data)

    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/{collection}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {"fields": firestore_fields}

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if not response.ok:
        print("Error inserting document:", response.text)
