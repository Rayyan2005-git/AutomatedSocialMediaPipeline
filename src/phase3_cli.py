import argparse
import json
import os
import sys
from dotenv import load_dotenv
from uploader import Uploader, UploadError

def mask_payload(payload):
    masked = payload.copy()
    if 'access_token' in masked:
        masked['access_token'] = '********'
    return masked

def main():
    # Fix Unicode output for Windows terminals (emojis)
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        
    # Ensure src is in the python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Phase 3: Upload to Instagram")
    parser.add_argument("--manifest", type=str, default="output/manifest.json", help="Path to manifest file")
    parser.add_argument("--live", action="store_true", help="Execute real upload (defaults to dry-run)")
    args = parser.parse_args()

    manifest_path = os.path.abspath(args.manifest)
    if not os.path.exists(manifest_path):
        print(f"Manifest not found at {manifest_path}")
        sys.exit(1)
        
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    # Determine schema format (Phase 2 nested vs flat dummy)
    items = manifest.get('files', manifest.get('items', []))
    
    gcs_bucket = os.environ.get("GCS_BUCKET_NAME")
    ig_token = os.environ.get("IG_ACCESS_TOKEN")
    ig_account = os.environ.get("IG_BUSINESS_ACCOUNT_ID")
    
    uploader = None
    if args.live:
        print("Running in LIVE mode. Real network calls will be made.")
        if not all([gcs_bucket, ig_token, ig_account]):
            print("ERROR: Missing required environment variables (GCS_BUCKET_NAME, IG_ACCESS_TOKEN, IG_BUSINESS_ACCOUNT_ID).")
            sys.exit(1)
        uploader = Uploader(gcs_bucket, ig_token, ig_account)
    else:
        print("Running in DRY-RUN mode. No real network calls will be made.")
        
    for item in items:
        # Handle both flat dummy schema and Phase 2 nested schema
        phase2_data = item.get('phase2', item)
        
        fidelity_passed = phase2_data.get('fidelityCheckPassed', False)
        generated_path = phase2_data.get('generatedPath')
        caption_base = phase2_data.get('caption', '')
        hashtags = phase2_data.get('hashtags', [])
        
        if isinstance(hashtags, list) and hashtags:
            caption = caption_base + "\n\n" + " ".join(hashtags)
        else:
            caption = caption_base
            
        print(f"\nProcessing file: {item.get('localPath', item.get('file_name', 'Unknown'))}")
        
        if not fidelity_passed:
            print("  ⏭️ Skipped: fidelityCheckPassed is false.")
            item['uploadStatus'] = "skipped_fidelity"
            continue
            
        if not generated_path:
            print("  ⏭️ Skipped: No generatedPath found.")
            item['uploadStatus'] = "skipped_no_path"
            continue
            
        abs_generated_path = os.path.abspath(os.path.join(os.path.dirname(manifest_path), '..', generated_path))
        if not os.path.exists(abs_generated_path):
            print(f"  ❌ Failed: File {abs_generated_path} does not exist.")
            item['uploadStatus'] = "failed_file_not_found"
            continue
            
        # Prepare payload
        payload = {
            "image_path": abs_generated_path,
            "caption": caption,
            "ig_business_account_id": ig_account if args.live else "dummy_ig_account",
            "access_token": ig_token if args.live else "dummy_token"
        }
        
        print(f"  Payload: {json.dumps(mask_payload(payload), indent=2)}")
        
        if not args.live:
            print("  ✅ Dry-run complete. (Would have posted)")
            item['uploadStatus'] = "dry_run"
        else:
            try:
                post_id = uploader.post_to_instagram(abs_generated_path, caption)
                print(f"  ✅ Posted! Post ID: {post_id}")
                item['uploadStatus'] = "posted"
                item['postId'] = post_id
            except Exception as e:
                print(f"  ❌ Failed: {e}")
                item['uploadStatus'] = "failed"
                item['uploadError'] = str(e)
                
    # Save manifest
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest updated at {manifest_path}")

if __name__ == "__main__":
    main()
