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

# 1. Rename the old one back to something else so it doesn't match
old_file = next((f for f in files if f['name'] == 'photo_Gift for Women - Purple Flask Kit_1.jpg'), None)
if old_file:
    print("Renaming old matched file back...")
    service.files().update(
        fileId=old_file['id'],
        body={'name': 'old_test_image.jpg'}
    ).execute()

# 2. Find a completely different file to rename
new_file = next((f for f in files if f['name'] != 'old_test_image.jpg' and 'Gift for Women' not in f['name']), None)

if new_file:
    new_name = f"photo_{theme}_2.jpg"
    print(f"Renaming completely different file '{new_file['name']}' to '{new_name}'...")
    service.files().update(
        fileId=new_file['id'],
        body={'name': new_name}
    ).execute()
    print("Rename successful!")
else:
    print("Could not find another file to rename.")
