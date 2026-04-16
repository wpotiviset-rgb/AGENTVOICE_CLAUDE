import os
import base64
import logging
from playwright.sync_api import sync_playwright
from pathlib import Path

# Path Config
BASE_DIR = Path(__file__).parent.parent.parent.absolute()
FONT_DIR = BASE_DIR / "Assets" / "Fonts"

# Font Priority
FONTS = [
    FONT_DIR / "NotoSansThai-Bold.ttf",
    FONT_DIR / "Sarabun-Bold.ttf"
]

class ThaiTextRenderer:
    def __init__(self, viewport_width=1080, viewport_height=1920):
        self.width = viewport_width
        self.height = viewport_height
        self.font_data = self._load_local_font()

    def _load_local_font(self):
        """Find and encode primary font to Base64 for CSS injection."""
        for font_path in FONTS:
            if font_path.exists():
                logging.info(f"🎨 Using Local Font: {font_path.name}")
                with open(font_path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
        return None

    def _generate_html(self, text, bg_image_path):
        """Create HTML with embedded font and background image."""
        bg_abs_path = os.path.abspath(bg_image_path)
        
        # Base64 Image to ensure it loads in Playwright set_content
        bg_base64 = ""
        if os.path.exists(bg_abs_path):
            with open(bg_abs_path, "rb") as f:
                bg_base64 = base64.b64encode(f.read()).decode()
        
        bg_url = f"data:image/png;base64,{bg_base64}"
        
        font_face = ""
        if self.font_data:
            font_face = f"""
            @font-face {{
                font-family: 'ThaiCustom';
                src: url(data:font/truetype;base64,{self.font_data}) format('truetype');
            }}
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                {font_face}
                body, html {{
                    margin: 0; padding: 0;
                    width: {self.width}px; height: {self.height}px;
                    overflow: hidden;
                    background-color: black;
                }}
                .background {{
                    position: absolute;
                    top: 0; left: 0;
                    width: 100%; height: 100%;
                    background-image: url('{bg_url}');
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                }}
                .overlay {{
                    position: absolute;
                    width: 100%; height: 100%;
                    background: rgba(0,0,0,0.3); /* Base dimming */
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    text-align: center;
                }}
                .text-box {{
                    width: 80%;
                    padding: 40px;
                    background: rgba(0, 0, 0, 0.6);
                    border-radius: 20px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                }}
                h1 {{
                    font-family: 'ThaiCustom', 'Sarabun', sans-serif;
                    color: white;
                    font-size: 80px;
                    margin: 0;
                    line-height: 1.4;
                    text-shadow: 2px 4px 10px rgba(0,0,0,0.8);
                }}
            </style>
        </head>
        <body>
            <div class="background"></div>
            <div class="overlay">
                <div class="text-box">
                    <h1>{text}</h1>
                </div>
            </div>
        </body>
        </html>
        """

    def render_scene(self, text, bg_image_path, output_path):
        """Bake text onto image using Playwright."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={'width': self.width, 'height': self.height})
                
                html_content = self._generate_html(text, bg_image_path)
                page.set_content(html_content)
                
                # Wait a small bit for font/image render (usually not needed for local)
                page.wait_for_timeout(500)
                
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                page.screenshot(path=output_path, full_page=True)
                browser.close()
                logging.info(f"✅ Baked Scene: {output_path}")
                return output_path
        except Exception as e:
            logging.error(f"❌ Error in TextRenderer: {e}")
            raise e

if __name__ == "__main__":
    pass
