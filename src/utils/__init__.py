import base64


def url_to_document_id(url: str) -> str:
    """Convert a URL to a Firestore-safe Base64-encoded document ID."""
    encoded = base64.urlsafe_b64encode(url.encode("utf-8")).decode("utf-8")
    return encoded.rstrip("=")
