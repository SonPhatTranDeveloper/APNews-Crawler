import json

import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account

from constants import FIREBASE_PROJECT_ID
from .firestore_client import FirestoreClient


def get_firestore_access_token(service_account_path: str) -> str:
    """Legacy function to get Firestore access token.
    
    Args:
        service_account_path (str): Path to the service account JSON file.
        
    Returns:
        str: OAuth2 access token.
    """
    client = FirestoreClient(service_account_path)
    return client.get_access_token()


def insert_document_firestore_rest(
    access_token: str,
    collection: str,
    document_id: str,
    document_data: dict,
    project_id: str = None,
) -> str:
    """Legacy function to insert a document into Firestore.
    
    Args:
        access_token (str): OAuth2 access token.
        collection (str): Collection name.
        document_id (str): Document ID.
        document_data (dict): Document data.
        project_id (str): Firebase/GCP project ID.
        
    Returns:
        str: JSON response from Firestore.
    """
    # Create a temporary client with the access token
    client = FirestoreClient("", project_id)
    client._access_token = access_token  # Set the access token directly
    
    return client.insert_document(collection, document_id, document_data)
