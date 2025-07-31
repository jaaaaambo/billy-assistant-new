import gspread
import os
import base64
import tempfile
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def get_credentials_from_env():
    base64_str = os.getenv("GOOGLE_CREDS_BASE64")
    if not base64_str:
        raise ValueError("Переменная окружения GOOGLE_CREDS_BASE64 не найдена.")

    creds_bytes = base64.b64decode(base64_str)

    # временный файл
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp:
        temp.write(creds_bytes)
        temp_path = temp.name

    return ServiceAccountCredentials.from_json_keyfile_name(temp_path, SCOPE)

def append_task_to_sheet(row):
    creds = get_credentials_from_env()
    client = gspread.authorize(creds)
    sheet = client.open("Billy Tasks").sheet1
    sheet.append_row(row)
