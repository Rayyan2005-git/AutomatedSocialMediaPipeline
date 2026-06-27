# Automated Social Media Pipeline

**Status: Phase 1 & 2 Complete, Phase 3 Pending**

This repository contains an automated social media pipeline. The project is broken down into three phases: Selection (Phase 1), Enhancement (Phase 2), and Upload (Phase 3).

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
   - `SPREADSHEET_ID`: The ID of the Google Sheet containing your content calendar.
   - `SHEET_RANGE`: The range to read (default: `Sheet1!A:B`).
   - `PHOTOROOM_API_KEY`: API Key for Photoroom Background Generation (Needed for Phase 2).

### Theme Configuration (Google Sheets)

The pipeline dynamically reads themes for the exact date from a Google Sheet.
The sheet must have exact ISO dates (`YYYY-MM-DD`) in the first column and the theme in the second column.

**Strict Matching:** 
If the current date is missing from the sheet, or if the Theme cell is empty, the pipeline will **fail loudly** and skip the run. It will not guess or fall back to a default theme.

### Usage

Run the Phase 1 CLI tool from the root of the project:

```bash
python src/cli.py --date 2026-06-24
```

---

## Phase 2: Enhancer (Scene Generation)

The enhancer reads the `manifest.json` from Phase 1, takes the original product photo, and generates a rich contextual background based on the matched theme using the **Photoroom API**. 

### Features
- **Photoroom Integration**: Generates ambient/lifestyle scenes while mathematically preserving 100% of the original foreground product.
- **Fidelity Check**: Uses OpenCV (ORB Feature Matching) to verify the original product remains undistorted in the generated image. Fails safely if the product is lost.
- **Formatting**: Automatically pads the resulting image to a perfect `4:5` aspect ratio for Instagram using Pillow.
- **Captions**: Generates a theme-aware caption and hashtags.

### Usage

After running Phase 1, run the Phase 2 CLI:

```bash
python src/phase2_cli.py
```

---

## Manifest Schema (Phase 1 + Phase 2)

The final output is saved to `output/manifest.json`.

```json
{
  "run_date": "2026-06-24",
  "weekday": "Wednesday",
  "themes_searched": ["minimalist-product"],
  "files": [
    {
      "drive_file_id": "dummy_id_5",
      "local_path": "output/downloads/photo_minimalist-product_1.jpg",
      "matched_theme": "minimalist-product",
      "mime_type": "image/jpeg",
      "file_name": "photo_minimalist-product_1.jpg",
      "phase2": {
        "generatedPath": "output/enhanced/enhanced_photo_minimalist-product_1.jpg",
        "generationPrompt": "minimalist-product, high quality contextual ambient background...",
        "fidelityCheckPassed": true,
        "policyRejected": false,
        "caption": "Keep it simple and stylish. Elevate your space with this clean design. ✨\n\n#minimalistproduct #product #newarrival #musthave",
        "aspectRatio": "4:5"
      }
    }
  ]
}
```
