import os
import requests
from dotenv import load_dotenv

def test_photoroom():
    load_dotenv()
    api_key = os.environ.get("PHOTOROOM_API_KEY")
    if not api_key:
        print("Error: PHOTOROOM_API_KEY not found in .env")
        return

    url = "https://image-api.photoroom.com/v2/edit"
    
    # Using the generated image as input
    input_image_path = r"C:\Users\Acer\.gemini\antigravity\brain\da88cbcc-c53d-4fad-87d1-29d83399b8f6\toy_truck_1782543424623.png"
    output_image_path = r"C:\Users\Acer\.gemini\antigravity\brain\da88cbcc-c53d-4fad-87d1-29d83399b8f6\photoroom_result.png"
    
    prompt = "A child happily playing with this toy, bright sunny living room, joyful atmosphere, high quality lifestyle photography, 8k, photorealistic"
    
    print("Calling Photoroom API...")
    
    with open(input_image_path, "rb") as f:
        response = requests.post(
            url,
            headers={"x-api-key": api_key},
            data={
                "background.prompt": prompt,
                "shadow.mode": "ai.soft"
            },
            files={"imageFile": f}
        )
        
    if response.status_code == 200:
        with open(output_image_path, "wb") as out_f:
            out_f.write(response.content)
        print(f"Success! Saved to {output_image_path}")
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    test_photoroom()
