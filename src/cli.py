import argparse
import datetime
import os
import sys

# Ensure src is in the python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from drive_client import DriveClient
from selector import ThemeSelector
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

    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'themes.json')
    selector = ThemeSelector(config_path)
    weekday, themes = selector.get_themes_for_date(target_date)
    
    print(f"Weekday: {weekday}, Themes to search: {themes}")

    if not themes:
        print("No themes configured for this weekday. Exiting.")
        return

    # Initialize Drive Client
    drive_folder_id = os.environ.get("DRIVE_FOLDER_ID", "dummy_folder_id")
    client = DriveClient()

    # List photos
    print(f"Listing photos in Drive folder: {drive_folder_id}")
    all_photos = client.list_photos(drive_folder_id)
    print(f"Found {len(all_photos)} photos total.")

    # Filter photos
    matched_photos = selector.filter_files(all_photos, themes)
    print(f"Matched {len(matched_photos)} photos against themes.")

    # Download photos
    downloads_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'downloads')
    os.makedirs(downloads_dir, exist_ok=True)

    for photo in matched_photos:
        local_path = os.path.join(downloads_dir, photo['name'])
        print(f"Downloading {photo['name']}...")
        client.download_file(photo['id'], local_path)
        # Store relative path for manifest
        photo['local_path'] = os.path.relpath(local_path, start=os.path.join(os.path.dirname(__file__), '..')).replace('\\', '/')

    # Write manifest
    manifest_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'manifest.json')
    writer = ManifestWriter(manifest_path)
    writer.write(target_date, weekday, themes, matched_photos)
    print(f"Manifest written to {manifest_path}")

if __name__ == "__main__":
    main()
