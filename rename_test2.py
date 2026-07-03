import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()
creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
folder_id = os.environ.get("DRIVE_FOLDER_ID")
theme = "Gift for Women - Purple Flask Kit"

creds = service_account.Credentials.from_service_account_file(
    creds_path, scopes=['https://www.googleapis.com/auth/drive']
)
service = build('drive', 'v3', credentials=creds)

query = f"'{folder_id}' in parents and mimeType contains 'image/' and trashed = false"
response = service.files().list(q=query, spaces='drive', fields='files(id, name, mimeType)').execute()
files = response.get('files', [])

if not files:
    print("No files found to rename.")
    exit()

# Find the file we renamed yesterday (photo_Gift for Women_1.jpg) and rename it again
file_to_rename = next((f for f in files if f['name'] == 'photo_Gift for Women_1.jpg'), files[0])
old_name = file_to_rename['name']
new_name = f"photo_{theme}_1.jpg"

print(f"Renaming '{old_name}' to '{new_name}'...")

service.files().update(
    fileId=file_to_rename['id'],
    body={'name': new_name}
).execute()

print("Rename successful!")
