# Automated Social Media Pipeline

**Status: Phase-1 in Progress**

This repository contains an automated social media pipeline. Phase 1 focuses on the **Selection** of photos from Google Drive based on daily themes.

## Phase 1: Selector

The selector pulls photos from a specified Google Drive folder that match the current day's theme, downloads them locally, and produces a manifest.

### Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables:**
   Copy `.env.example` to `.env` and fill in the required values:
   - `GOOGLE_APPLICATION_CREDENTIALS`: Path to your Google Service Account JSON file.
   - `DRIVE_FOLDER_ID`: The ID of the Google Drive folder containing the photos.

### Theme Configuration

Themes are configured in `config/themes.json`. The keys are weekdays, and the values are lists of keywords.

Example:
```json
{
  "Monday": ["motivation", "sale"]
}
```

### Usage

Run the CLI tool from the root of the project:

```bash
python src/cli.py --date 2026-06-20
```

By default, it uses today's date. The `--date` argument is optional and can be used to test specific days (format `YYYY-MM-DD`).

### Manifest Schema

The output will be saved to `output/manifest.json`. The schema is designed for subsequent phases (enhancement and upload).

```json
{
  "run_date": "2026-06-20",
  "weekday": "Saturday",
  "themes_searched": ["lifestyle", "relax"],
  "files": [
    {
      "drive_file_id": "1A2B3C4D...",
      "local_path": "output/downloads/file.jpg",
      "matched_theme": "lifestyle",
      "mime_type": "image/jpeg",
      "file_name": "file.jpg"
    }
  ]
}
```
