import os
import requests
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from google.cloud import storage

class UploadError(Exception):
    pass

class Uploader:
    def __init__(self, gcs_bucket_name, ig_access_token, ig_business_account_id):
        self.gcs_bucket_name = gcs_bucket_name
        self.ig_access_token = ig_access_token
        self.ig_business_account_id = ig_business_account_id
        try:
            self.storage_client = storage.Client()
        except Exception as e:
            print(f"Warning: Could not initialize Google Cloud Storage client. {e}")
            self.storage_client = None

    def upload_to_gcs(self, local_path):
        """Uploads a local image to Google Cloud Storage and returns the public URL."""
        if not self.storage_client:
            raise UploadError("Google Cloud Storage client is not initialized.")
            
        bucket = self.storage_client.bucket(self.gcs_bucket_name)
        blob_name = os.path.basename(local_path)
        blob = bucket.blob(blob_name)
        
        print(f"  -> Uploading to GCS bucket: {self.gcs_bucket_name}/{blob_name}")
        blob.upload_from_filename(local_path)
        
        print("  -> Making GCS object public...")
        blob.make_public()
        
        return blob.public_url, blob_name

    def delete_from_gcs(self, blob_name):
        """Deletes the object from GCS to save storage space."""
        try:
            bucket = self.storage_client.bucket(self.gcs_bucket_name)
            blob = bucket.blob(blob_name)
            blob.delete()
            print(f"  -> Cleaned up GCS object: {blob_name}")
        except Exception as e:
            print(f"  -> Warning: Failed to clean up GCS object {blob_name}: {e}")

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(UploadError)
    )
    def create_ig_media_container(self, image_url, caption):
        """Step 1: Create media container on Instagram."""
        url = f"https://graph.instagram.com/v25.0/{self.ig_business_account_id}/media"
        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.ig_access_token
        }
        
        response = requests.post(url, data=payload)
        data = response.json()
        
        if response.status_code == 200 and 'id' in data:
            return data['id']
        else:
            raise UploadError(f"IG Media Creation failed: {data}")

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(UploadError)
    )
    def publish_ig_media(self, creation_id):
        """Step 2: Publish the media container on Instagram."""
        url = f"https://graph.instagram.com/v25.0/{self.ig_business_account_id}/media_publish"
        payload = {
            "creation_id": creation_id,
            "access_token": self.ig_access_token
        }
        
        response = requests.post(url, data=payload)
        data = response.json()
        
        if response.status_code == 200 and 'id' in data:
            return data['id']
        else:
            raise UploadError(f"IG Media Publish failed: {data}")

    def post_to_instagram(self, local_path, caption):
        """End-to-end process: GCS -> IG Create -> IG Publish -> GCS Delete."""
        public_url, blob_name = self.upload_to_gcs(local_path)
        print(f"  -> GCS Public URL: {public_url}")
        
        try:
            print("  -> Creating Instagram media container...")
            creation_id = self.create_ig_media_container(public_url, caption)
            
            print("  -> Publishing to Instagram...")
            post_id = self.publish_ig_media(creation_id)
            return post_id
        finally:
            # Always attempt to clean up the GCS object, even if IG fails
            self.delete_from_gcs(blob_name)
