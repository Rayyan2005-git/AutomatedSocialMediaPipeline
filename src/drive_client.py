import os
import io
from google.oauth2 import service_account
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

class DriveClient:
    def __init__(self):
        creds = None
        try:
            # First attempt to use application default credentials, which will pick up GOOGLE_APPLICATION_CREDENTIALS
            creds, project = google.auth.default(scopes=['https://www.googleapis.com/auth/drive.readonly'])
            self.service = build('drive', 'v3', credentials=creds)
        except Exception as e:
            print(f"Warning: Could not load default credentials: {e}")
            print("Running in mock mode. Please set GOOGLE_APPLICATION_CREDENTIALS to a valid service account JSON file.")
            self.service = None

    def list_photos(self, folder_id, theme=None):
        """Lists only photo files in the specified Drive folder or Theme subfolder."""
        if not self.service:
            print("Mock mode: Returning dummy photo list.")
            return [], False

        target_folder_id = folder_id
        is_subfolder = False
        
        # If a theme is provided, try to find a subfolder matching the theme
        if theme:
            folder_query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and name = '{theme}' and trashed = false"
            try:
                folder_response = self.service.files().list(
                    q=folder_query, spaces='drive', fields='files(id, name)'
                ).execute()
                subfolders = folder_response.get('files', [])
                if subfolders:
                    target_folder_id = subfolders[0]['id']
                    is_subfolder = True
                    print(f"Found theme subfolder: '{theme}' (ID: {target_folder_id})")
                else:
                    print(f"Warning: No subfolder named '{theme}' found. Defaulting to root folder.")
            except Exception as e:
                print(f"Warning: Error searching for subfolder: {e}")

        results = []
        page_token = None
        # Query: only images, in the target folder, not trashed
        query = f"'{target_folder_id}' in parents and mimeType contains 'image/' and trashed = false"
        
        while True:
            response = self.service.files().list(
                q=query,
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType)',
                pageToken=page_token
            ).execute()
            
            results.extend(response.get('files', []))
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        return results, is_subfolder

    def download_file(self, file_id, local_path):
        """Downloads a file from Drive to the local path."""
        if not self.service:
            print(f"Mock mode: Skipping download for {file_id}. Creating dummy file at {local_path}.")
            with open(local_path, 'w') as f:
                f.write("dummy content")
            return

        request = self.service.files().get_media(fileId=file_id)
        with io.FileIO(local_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
