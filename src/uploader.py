import os
import requests
import base64
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

class UploadError(Exception):
    pass

class Uploader:
    def __init__(self, imgbb_api_key, ig_access_token, ig_business_account_id):
        self.imgbb_api_key = imgbb_api_key
        self.ig_access_token = ig_access_token
        self.ig_business_account_id = ig_business_account_id

    def upload_to_imgbb(self, local_path):
        """Uploads a local image to ImgBB and returns the public URL."""
        if not self.imgbb_api_key:
            raise UploadError("IMGBB_API_KEY is not set.")
            
        with open(local_path, "rb") as file:
            url = "https://api.imgbb.com/1/upload"
            payload = {
                "key": self.imgbb_api_key,
                "image": base64.b64encode(file.read()).decode('utf-8')
            }
            response = requests.post(url, data=payload)
            
            if response.status_code == 200:
                return response.json()['data']['url']
            else:
                raise UploadError(f"ImgBB upload failed: {response.text}")

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
        """End-to-end process: ImgBB -> IG Create -> IG Publish."""
        print(f"  -> Uploading {local_path} to ImgBB...")
        public_url = self.upload_to_imgbb(local_path)
        print(f"  -> ImgBB URL: {public_url}")
        
        print("  -> Creating Instagram media container...")
        creation_id = self.create_ig_media_container(public_url, caption)
        
        print("  -> Publishing to Instagram...")
        post_id = self.publish_ig_media(creation_id)
        
        return post_id
