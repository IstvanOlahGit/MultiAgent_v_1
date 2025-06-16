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


def list_doc_names_range(start: int = 1, end: int = 10, return_count_only: bool = False) -> int | list[str]:
    service = get_drive_service()
    query = "mimeType='application/vnd.google-apps.document'"
    page_token = None
    doc_names = []

    while True:
        response = service.files().list(
            q=query,
            spaces="drive",
            fields="nextPageToken, files(id, name)",
            pageToken=page_token,
            pageSize=100
        ).execute()

        files = response.get("files", [])
        if not files:
            break

        doc_names.extend(files)
        page_token = response.get("nextPageToken")
        if page_token is None:
            break

    if return_count_only:
        return len(doc_names)

    sliced = doc_names[start - 1:end]
    return [doc["name"] for doc in sliced]