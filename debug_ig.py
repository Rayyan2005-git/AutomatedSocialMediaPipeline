import os
import requests
from dotenv import load_dotenv

load_dotenv()
ig_token = os.environ.get("IG_ACCESS_TOKEN")
ig_account = os.environ.get("IG_BUSINESS_ACCOUNT_ID")
public_url = "https://upload.wikimedia.org/wikipedia/commons/4/41/Sunflower_from_Silesia2.jpg"
caption = "Test caption"

url = f"https://graph.instagram.com/v25.0/{ig_account}/media"
payload = {
    "image_url": public_url,
    "caption": caption,
    "access_token": ig_token
}

response = requests.post(url, data=payload)
print(response.status_code)
print(response.content.decode('utf-8', errors='ignore'))
