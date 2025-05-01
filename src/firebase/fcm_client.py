import json
import os
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2 import service_account

from constants import FIREBASE_PROJECT_ID


class FCMClient:
    """Firebase Cloud Messaging client for sending notifications."""

    def __init__(
        self, service_account_path: str, project_id: str = FIREBASE_PROJECT_ID
    ):
        """Initialize the FCM client.

        Args:
            service_account_path (str): Path to the service account JSON file.
            project_id (str): Firebase/GCP project ID.
        """
        self.service_account_path = service_account_path
        self.project_id = project_id
        self._access_token = None

    def get_access_token(self) -> str:
        """Get an access token for FCM operations.

        Returns:
            str: OAuth2 access token.
        """
        if not self._access_token:
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_path,
                scopes=["https://www.googleapis.com/auth/firebase.messaging"],
            )
            credentials.refresh(Request())
            self._access_token = credentials.token
        return self._access_token

    def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict] = None,
    ) -> Dict:
        """Send a notification to a specific topic.

        Args:
            topic (str): The topic to send the notification to (e.g., 'news', 'sports').
            title (str): Notification title.
            body (str): Notification body text.
            data (Optional[Dict]): Additional data payload to send with notification.

        Returns:
            Dict: Response from FCM API.

        Raises:
            Exception: If the notification fails to send.
        """
        url = f"https://fcm.googleapis.com/v1/projects/{self.project_id}/messages:send"

        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json",
        }

        message = {
            "message": {
                "topic": topic,
                "notification": {
                    "title": title,
                    "body": body,
                },
                "android": {
                    "notification": {
                        "click_action": "FLUTTER_NOTIFICATION_CLICK",
                        "sound": "default",
                    }
                },
                "apns": {"payload": {"aps": {"sound": "default"}}},
            }
        }

        if data:
            message["message"]["data"] = {str(k): str(v) for k, v in data.items()}

        response = requests.post(url, headers=headers, data=json.dumps(message))

        if response.ok:
            return response.json()
        else:
            raise Exception(
                f"Error sending notification: {response.status_code} - {response.text}"
            )

    def send_to_tokens(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict] = None,
    ) -> Dict:
        """Send a notification to specific device tokens.

        Args:
            tokens (List[str]): List of FCM device tokens to send to.
            title (str): Notification title.
            body (str): Notification body text.
            data (Optional[Dict]): Additional data payload to send with notification.

        Returns:
            Dict: Response from FCM API.

        Raises:
            Exception: If the notification fails to send.
        """
        url = f"https://fcm.googleapis.com/v1/projects/{self.project_id}/messages:send"

        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json",
        }

        responses = []
        for token in tokens:
            message = {
                "message": {
                    "token": token,
                    "notification": {
                        "title": title,
                        "body": body,
                    },
                    "android": {
                        "notification": {
                            "click_action": "FLUTTER_NOTIFICATION_CLICK",
                            "sound": "default",
                        }
                    },
                    "apns": {"payload": {"aps": {"sound": "default"}}},
                }
            }

            if data:
                message["message"]["data"] = {str(k): str(v) for k, v in data.items()}

            response = requests.post(url, headers=headers, data=json.dumps(message))

            if response.ok:
                responses.append(response.json())
            else:
                print(f"Failed to send to token {token}: {response.text}")

        return {"responses": responses}


if __name__ == "__main__":
    # Test run the FCM client
    load_dotenv()
    fcm_client = FCMClient(
        service_account_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )
    fcm_client.send_to_topic(
        "news_channel", "Test Notification", "This is a test notification"
    )
