import os
import requests
import logging
from dotenv import load_dotenv
from pathlib import Path

# Load env for API keys
BASE_DIR = Path(__file__).parent.parent.parent.absolute()
load_dotenv(BASE_DIR / ".env")

FALAI_API_KEY = os.getenv("FALAI_API_KEY")

class VisualGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or FALAI_API_KEY

    def generate_image(self, prompt, output_path, image_size="portrait_16_9"):
        """Call Fal.ai (FLUX) to generate high-quality images."""
        if not self.api_key:
            logging.error("⚠️ FALAI_API_KEY missing. Skipping image generation.")
            return False
            
        logging.info(f"🎨 Generating Image for: '{prompt[:40]}...'")
        
        url = "https://fal.run/fal-ai/flux/schnell"
        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": f"{prompt}, high quality, cinematic lighting, professional photography, vertical 9:16",
            "image_size": image_size,
            "num_inference_steps": 4,
            "num_images": 1
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                image_url = data.get("images", [{}])[0].get("url")
                if image_url:
                    img_data = requests.get(image_url).content
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, "wb") as f:
                        f.write(img_data)
                    logging.info(f"✅ Image Saved: {output_path}")
                    return True
            else:
                logging.error(f"❌ Fal.ai Error: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"❌ Error in VisualGenerator: {e}")
            
        return False
