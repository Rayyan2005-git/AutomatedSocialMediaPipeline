import os
import requests
import cv2
from PIL import Image, ImageOps

class Enhancer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://image-api.photoroom.com/v2/edit"

    def generate_scene(self, input_image_path, prompt, output_image_path):
        """Calls Photoroom API to generate an ambient background based on prompt."""
        if not self.api_key:
            # Fallback mock mode for testing without keys
            print(f"Mock mode: Enhancing {input_image_path} with prompt {prompt}")
            # Just copy the original to output to simulate a generated image
            img = Image.open(input_image_path)
            img.save(output_image_path)
            return output_image_path

        # Use the direct prompt from the Google Sheet
        
        print(f"Calling Photoroom API for {input_image_path}...")
        
        try:
            with open(input_image_path, "rb") as f:
                response = requests.post(
                    self.url,
                    headers={"x-api-key": self.api_key},
                    data={
                        "background.prompt": prompt,
                        "shadow.mode": "ai.soft",
                        "padding": "0.15"
                    },
                    files={"imageFile": f}
                )
            
            if response.status_code == 200:
                with open(output_image_path, "wb") as out_f:
                    out_f.write(response.content)
                return output_image_path
            else:
                print(f"Error {response.status_code}: {response.text}")
                
                # Check for policy rejections
                if "policy" in response.text.lower() or response.status_code in [403, 400]:
                    print("Policy rejection detected. Skipping this image.")
                    return "POLICY_REJECTED"
                
                return None
        except Exception as e:
            print(f"Exception during API call: {e}")
            return None

    def check_fidelity(self, original_path, enhanced_path, min_matches=50):
        """
        Uses ORB feature matching to ensure the product foreground is still present and undistorted.
        Since Photoroom composites the exact product on top, feature matching will easily find the product.
        """
        print("Running fidelity check (ORB Feature Matching)...")
        img1 = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(enhanced_path, cv2.IMREAD_GRAYSCALE)
        
        if img1 is None or img2 is None:
            return False
            
        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)
        
        if des1 is None or des2 is None:
            return False
            
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        
        print(f"Found {len(matches)} matching features.")
        return len(matches) > min_matches

    def pad_image(self, image_path, ratio="4:5"):
        """Pads an image with white borders to fit the exact aspect ratio (e.g., for Instagram)."""
        img = Image.open(image_path)
        w, h = img.size
        
        if ratio == "4:5":
            target_w = w
            target_h = int(w * 5 / 4)
            if target_h < h:
                target_h = h
                target_w = int(h * 4 / 5)
        elif ratio == "1:1":
            target_w = max(w, h)
            target_h = max(w, h)
        else:
            return image_path
            
        delta_w = target_w - w
        delta_h = target_h - h
        
        # Only pad if necessary
        if delta_w > 0 or delta_h > 0:
            padding = (delta_w // 2, delta_h // 2, delta_w - (delta_w // 2), delta_h - (delta_h // 2))
            new_img = ImageOps.expand(img, padding, fill="white")
            if new_img.mode in ("RGBA", "P"):
                new_img = new_img.convert("RGB")
            new_img.save(image_path)
            print(f"Padded image to {ratio} ({target_w}x{target_h})")
            
        return image_path

    def generate_caption(self, theme, prompt):
        """Generates a theme-aware caption and hashtags using Gemini AI."""
        from google import genai
        
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_api_key or gemini_api_key == "your_gemini_api_key_here":
            print("No GEMINI_API_KEY found, falling back to basic caption.")
            return f"Check out this amazing product for your {theme} needs! ✨\n\n#{theme.replace('-', '').replace(' ', '')} #product #newarrival #musthave"
            
        try:
            client = genai.Client(api_key=gemini_api_key)
            
            ai_prompt = (
                f"Write a highly engaging, luxury-brand Instagram caption for a product. "
                f"The product's theme is '{theme}'. The visual vibe is described as: '{prompt}'. "
                f"Include 3-5 relevant emojis and 5-7 popular hashtags. "
                f"Keep it under 3 short paragraphs. No generic marketing speak, make it feel authentic."
            )
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=ai_prompt,
            )
            if response.text:
                return response.text.strip()
        except Exception as e:
            print(f"Gemini API Error: {e}")
            
        # Fallback
        return f"Check out this amazing product for your {theme} needs! ✨\n\n#{theme.replace('-', '').replace(' ', '')} #product #newarrival #musthave"
