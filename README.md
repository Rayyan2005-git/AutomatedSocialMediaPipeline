# Automated Social Media Pipeline

**Status: 100% Complete (Phase 1, Phase 2, & Phase 3)**

This repository contains a fully automated, end-to-end social media pipeline. The project is broken down into three phases: 
1. **Selection (Phase 1):** Connects to Google Sheets for the content calendar and Google Drive to pull the corresponding product images.
2. **Enhancement (Phase 2):** Connects to the Photoroom AI API to generate premium lifestyle backgrounds around your product, and the Google Gemini 2.5 Flash API to write engaging luxury-brand captions.
3. **Upload (Phase 3):** Connects to Google Cloud Storage (GCS) to temporarily host the image, and then pushes it directly to your Instagram Feed via the Instagram Graph API.

---

## Complete Setup Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Google Cloud Service Account
You must have a Google Cloud Project with the following APIs enabled:
- **Google Sheets API**
- **Google Drive API**

You must create a Service Account JSON Key and place it in the `config/` directory.

### 3. Google Cloud Storage Bucket
You must create a Google Cloud Storage bucket to temporarily host the images for Instagram.
- **IMPORTANT**: Make sure "Enforce public access prevention on this bucket" is **UNCHECKED**.
- Grant your Service Account the **Storage Object Admin** role on the bucket.

### 4. Environment Variables
Copy `.env.example` to `.env` and fill in the required values:

```env
# Phase 1: Google Drive & Sheets
GOOGLE_APPLICATION_CREDENTIALS=config/google_credentials.json
DRIVE_FOLDER_ID=your_drive_folder_id_here
SPREADSHEET_ID=your_google_sheet_id_here
SHEET_RANGE=Sheet1!A:C

# Phase 2: Photoroom AI & Gemini
PHOTOROOM_API_KEY=your_photoroom_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Phase 3: GCS & Instagram API
GCS_BUCKET_NAME=your_gcs_bucket_name_here
IG_ACCESS_TOKEN=your_ig_access_token_here
IG_BUSINESS_ACCOUNT_ID=your_ig_business_account_id_here
```

---

## Phase 1: Selector

The selector dynamically reads themes and exact generation prompts for the exact date from a Google Sheet. It then pulls matching photos from the Google Drive folder, downloads them locally, and produces a `manifest.json`.

**Usage:**
```bash
# Runs for today's date by default
python src/cli.py 

# Or run for a specific date
python src/cli.py --date 2026-07-03
```

---

## Phase 2: Enhancer (Scene Generation)

The enhancer reads the manifest, takes the original product photo, and generates a rich contextual background based on the matched theme using the **Photoroom API**. It then generates a luxury-brand Instagram caption using the **Gemini 2.5 Flash API**.

**Features:**
- **Photoroom Integration**: Generates ambient/lifestyle scenes while mathematically preserving 100% of the original foreground product.
- **Gemini Captions**: Generates context-aware, engaging captions complete with emojis and hashtags.
- **Formatting**: Automatically pads the resulting image to a perfect `4:5` aspect ratio for Instagram (1000x1250).

**Usage:**
```bash
python src/phase2_cli.py
```

---

## Phase 3: Uploader (Instagram Publishing)

The final phase reads the completed manifest and handles publishing to Instagram. Since Instagram requires a public URL, this phase temporarily uses Google Cloud Storage.

**Features:**
- **Signed URLs:** Uploads the image to GCS and generates a temporary 15-minute Signed URL to bypass strict bucket ACL restrictions.
- **Instagram API:** Executes the 2-step media container creation and publishing flow.
- **Auto-Cleanup:** Instantly deletes the image from your GCS bucket as soon as the post succeeds, ensuring you don't pay for unnecessary storage.
- **Dry-Run Mode:** Safely test the payload generation without making any network calls to Instagram.

**Usage:**
```bash
# Dry Run (Safe Test - No Network Calls)
python src/phase3_cli.py --manifest output/manifest.json

# Live Run (Will post to your actual Instagram Feed!)
python src/phase3_cli.py --manifest output/manifest.json --live
```
