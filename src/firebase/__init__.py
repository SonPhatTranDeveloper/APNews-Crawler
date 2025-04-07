import firebase_admin
from firebase_admin import credentials, firestore


def init_firebase(service_account_path: str):
    """Initializes the Firebase app using the provided service account key.

    Args:
        service_account_path (str): The path to the Firebase service account JSON key file.

    Note:
        This function checks if Firebase is already initialized to avoid duplicate initialization.
    """
    if not firebase_admin._apps:
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)


def insert_document(
    service_account_path: str, collection_name: str, data: dict, doc_id: str = None
):
    """Inserts a document into a Firebase Firestore collection.

    Args:
        service_account_path (str): Path to the Firebase service account JSON key file.
        collection_name (str): Name of the Firestore collection to insert into.
        data (dict): The document data to insert.
        doc_id (str, optional): A custom document ID. If not provided, Firestore will auto-generate one.

    Returns:
        str: The ID of the inserted document.

    Raises:
        ValueError: If the data is not a dictionary.
    """
    if not isinstance(data, dict):
        raise ValueError("data must be a dictionary")

    init_firebase(service_account_path)
    db = firestore.client()
    collection_ref = db.collection(collection_name)

    if doc_id:
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(data)
        print(f"Document inserted with ID: {doc_id}")
        return doc_id
    else:
        doc_ref = collection_ref.add(data)
        doc_id = doc_ref[1].id
        print(f"Document added with auto-generated ID: {doc_id}")
        return doc_id
