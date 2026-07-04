import os
from PIL import Image, ImageOps
from google import genai

class Enhancer:
    def __init__(self):
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")

    def generate_scene(self, input_image_path, prompt, output_image_path):
        """Calls Photoroom API to generate a scene around the source image."""
        photoroom_api_key = os.environ.get("PHOTOROOM_API_KEY")
        
        if not photoroom_api_key or photoroom_api_key == "your_photoroom_api_key_here":
            print(f"Mock mode: Enhancing {input_image_path} with prompt {prompt}")
            # Just copy the original to output to simulate a generated image
            img = Image.open(input_image_path)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(output_image_path)
            return output_image_path

        print(f"Calling Photoroom API for background replacement...")
        
        try:
            import requests
            url = "https://image-api.photoroom.com/v2/edit"
            headers = {"x-api-key": photoroom_api_key}
            
            # Use 'background.prompt' to instruct Photoroom on the background scene
            data = {
                "background.prompt": prompt,
                "padding": "0.15",
                "outputSize": "1000x1250" # roughly 4:5
            }
            
            with open(input_image_path, "rb") as f:
                files = {"imageFile": f}
                response = requests.post(url, headers=headers, data=data, files=files)
            
            if response.status_code == 200:
                with open(output_image_path, "wb") as out_file:
                    out_file.write(response.content)
                print("Successfully generated image with Photoroom.")
                return output_image_path
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Exception during Photoroom Image Generation: {e}")
            return None

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
        if not self.gemini_api_key or self.gemini_api_key == "your_gemini_api_key_here":
            print("No GEMINI_API_KEY found, falling back to basic caption.")
            return f"Check out this amazing product for your {theme} needs! ✨\n\n#{theme.replace('-', '').replace(' ', '')} #product #newarrival #musthave"
            
        try:
            client = genai.Client(api_key=self.gemini_api_key)
            
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
