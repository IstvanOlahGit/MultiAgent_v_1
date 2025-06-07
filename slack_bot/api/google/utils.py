from google.oauth2 import service_account
from googleapiclient.discovery import build

from slack_bot.core.config import settings


def get_drive_service():
    creds = service_account.Credentials.from_service_account_info(
        settings.SERVICE_ACCOUNT_INFO,
        scopes=settings.SCOPES
    )
    return build("drive", "v3", credentials=creds)


def find_doc_by_name(doc_name: str) -> str | None:
    service = get_drive_service()
    query = f"name contains '{doc_name}'"
    results = service.files().list(q=query, pageSize=1, fields="files(id, name)").execute()
    files = results.get("files", [])
    if not files:
        return None
    return f"https://docs.google.com/document/d/{files[0]['id']}/edit"

