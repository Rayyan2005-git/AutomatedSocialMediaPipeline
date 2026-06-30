import google.auth
from googleapiclient.discovery import build

class SheetsClient:
    def __init__(self):
        creds = None
        try:
            creds, project = google.auth.default(scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
            self.service = build('sheets', 'v4', credentials=creds)
        except Exception as e:
            print(f"Warning: Could not load default credentials for Sheets: {e}")
            self.service = None

    def get_sheet_data(self, spreadsheet_id, range_name):
        """Fetches rows from the Google Sheet."""
        if not self.service:
            print("Mock mode: Returning dummy Google Sheet data.")
            return [
                ["Date", "Theme", "Generation Prompt"],
                ["2026-06-24", "minimalist-product", "Product on a clean white marble podium, soft studio lighting"],
                ["2026-06-25", "gifting-occasion", "An adult's hands wrapping this toy as a gift, warm cozy room, holiday lighting"],
                ["2026-06-26", "lifestyle-shelf", "Product displayed on a stylish wooden shelf, plants in background"],
                ["2026-06-27", "", ""], # Empty theme test
            ]

        try:
            sheet = self.service.spreadsheets()
            result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
            values = result.get('values', [])
            return values
        except Exception as e:
            print(f"Error fetching from Google Sheets: {e}")
            return []
