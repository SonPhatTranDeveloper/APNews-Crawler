import json
from typing import Any, Dict

import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account

from constants import FIREBASE_PROJECT_ID
from .base_client import BaseFirebaseClient


from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseFirebaseClient(ABC):
    """Abstract base class for Firebase operations."""

    @abstractmethod
    def get_access_token(self) -> str:
        """Get an access token for Firebase operations.

        Returns:
            str: OAuth2 access token.
        """
        pass

    @abstractmethod
    def insert_document(
        self,
        collection: str,
        document_id: str,
        document_data: Dict[str, Any],
    ) -> str:
        """Insert a document into Firebase.

        Args:
            collection (str): Collection name.
            document_id (str): Document ID.
            document_data (Dict[str, Any]): Document data.

        Returns:
            str: Response from Firebase.
        """
        pass


class FirestoreClient(BaseFirebaseClient):
    """Firestore implementation of the Firebase client."""

    def __init__(
        self, service_account_path: str, project_id: str = FIREBASE_PROJECT_ID
    ):
        """Initialize the Firestore client.

        Args:
            service_account_path (str): Path to the service account JSON file.
            project_id (str): Firebase/GCP project ID.
        """
        self.service_account_path = service_account_path
        self.project_id = project_id
        self._access_token = None

    def get_access_token(self) -> str:
        """Get an access token for Firestore operations.

        Returns:
            str: OAuth2 access token.
        """
        if not self._access_token:
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_path,
                scopes=["https://www.googleapis.com/auth/datastore"],
            )
            credentials.refresh(Request())
            self._access_token = credentials.token
        return self._access_token

    def _wrap_value(self, value: Any) -> Dict[str, Any]:
        """Convert a Python value to Firestore format.

        Args:
            value (Any): Python value to convert.

        Returns:
            Dict[str, Any]: Firestore-formatted value.

        Raises:
            TypeError: If the value type is not supported.
        """
        if isinstance(value, str):
            return {"stringValue": value}
        elif isinstance(value, bool):
            return {"booleanValue": value}
        elif isinstance(value, int):
            return {"integerValue": str(value)}
        elif isinstance(value, float):
            return {"doubleValue": value}
        elif isinstance(value, list):
            return {"arrayValue": {"values": [self._wrap_value(v) for v in value]}}
        elif isinstance(value, dict):
            return {"mapValue": {"fields": self._to_firestore_fields(value)}}
        elif value is None:
            return {"nullValue": None}
        else:
            raise TypeError(f"Unsupported type: {type(value)} for value: {value}")

    def _to_firestore_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a Python dictionary to Firestore fields format.

        Args:
            data (Dict[str, Any]): Python dictionary to convert.

        Returns:
            Dict[str, Any]: Firestore fields format.
        """
        return {key: self._wrap_value(val) for key, val in data.items()}

    def insert_document(
        self,
        collection: str,
        document_id: str,
        document_data: Dict[str, Any],
    ) -> str:
        """Insert a document into Firestore.

        Args:
            collection (str): Firestore collection name.
            document_id (str): Document ID.
            document_data (Dict[str, Any]): Document data.

        Returns:
            str: JSON response from Firestore.

        Raises:
            Exception: If the document insertion fails.
        """
        access_token = self.get_access_token()
        firestore_fields = self._to_firestore_fields(document_data)

        url = (
            f"https://firestore.googleapis.com/v1/projects/{self.project_id}/"
            f"databases/(default)/documents/{collection}/{document_id}"
        )

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        payload = {"fields": firestore_fields}
        response = requests.patch(url, headers=headers, data=json.dumps(payload))

        if response.ok:
            return response.text
        else:
            raise Exception(
                f"Error inserting document: {response.status_code} - {response.text}"
            )
