import argparse
import datetime
import os
import sys

# Ensure src is in the python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from drive_client import DriveClient
from sheets_client import SheetsClient
from selector import SheetThemeSelector
from manifest_writer import ManifestWriter

def main():
    # Load .env variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Phase 1: Photo Selector from Google Drive")
    parser.add_argument("--date", type=str, help="Date to run the selection for (YYYY-MM-DD). Defaults to today.", default=None)
    args = parser.parse_args()

    if args.date:
        target_date = datetime.datetime.strptime(args.date, "%Y-%m-%d").date()
    else:
        target_date = datetime.date.today()

    print(f"Running selection pipeline for date: {target_date}")

    # Fetch themes from Google Sheets
    spreadsheet_id = os.environ.get("SPREADSHEET_ID", "dummy_spreadsheet_id")
    sheet_range = os.environ.get("SHEET_RANGE", "Sheet1!A:C")
    
    print(f"Fetching themes from Google Sheet ID: {spreadsheet_id}, Range: {sheet_range}")
    sheets_client = SheetsClient()
    sheet_data = sheets_client.get_sheet_data(spreadsheet_id, sheet_range)
    
    selector = SheetThemeSelector(sheet_data)
    theme, prompt, product_folder, error_msg = selector.get_theme_for_date(target_date)

    if error_msg:
        print(f"ERROR: {error_msg} Skipping run.")
        sys.exit(1)

    print(f"Theme to search: '{theme}', Prompt: '{prompt}', Folder: '{product_folder}'")

    # Initialize Drive Client
    drive_folder_id = os.environ.get("DRIVE_FOLDER_ID", "dummy_folder_id")
    drive_client = DriveClient()

    # List photos
    print(f"Listing photos in Drive folder: {drive_folder_id}")
    all_photos, is_subfolder = drive_client.list_photos(drive_folder_id, theme=product_folder)
    print(f"Found {len(all_photos)} photos total.")

    # Filter photos
    matched_photos = selector.filter_files(all_photos, theme, prompt, is_subfolder=is_subfolder)
    print(f"Matched {len(matched_photos)} photos against theme '{theme}'.")

    # Download photos
    downloads_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'downloads')
    os.makedirs(downloads_dir, exist_ok=True)

    for photo in matched_photos:
        local_path = os.path.join(downloads_dir, photo['name'])
        print(f"Downloading {photo['name']}...")
        drive_client.download_file(photo['id'], local_path)
        # Store relative path for manifest
        photo['local_path'] = os.path.relpath(local_path, start=os.path.join(os.path.dirname(__file__), '..')).replace('\\', '/')

    # Write manifest
    manifest_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'manifest.json')
    writer = ManifestWriter(manifest_path)
    weekday = target_date.strftime("%A")
    writer.write(target_date, weekday, [theme], matched_photos)
    print(f"Manifest written to {manifest_path}")

if __name__ == "__main__":
    main()
