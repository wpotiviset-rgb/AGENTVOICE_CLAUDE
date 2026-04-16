import os
import requests
import subprocess
import sys
from pathlib import Path

# Config
BASE_DIR = Path(__file__).parent.parent.absolute()
FONT_DIR = BASE_DIR / "Assets" / "Fonts"
NOTO_SAN_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansThai/NotoSansThai-Bold.ttf"

def setup_fonts():
    """Download Noto Sans Thai if missing."""
    print("--- 📦 Font Setup Stage ---")
    os.makedirs(FONT_DIR, exist_ok=True)
    target = FONT_DIR / "NotoSansThai-Bold.ttf"
    
    if not target.exists():
        print(f"📥 Downloading Noto Sans Thai from: {NOTO_SAN_URL}")
        try:
            response = requests.get(NOTO_SAN_URL, timeout=30)
            if response.status_code == 200:
                with open(target, "wb") as f:
                    f.write(response.content)
                print(f"✅ Downloaded: {target}")
            else:
                print(f"❌ Failed to download font: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Error downloading font: {e}")
    else:
        print(f"✅ Noto Sans Thai already exists: {target}")

def setup_playwright():
    """Install Playwright browsers."""
    print("\n--- 🌐 Playwright Browser Setup Stage ---")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("✅ Playwright Chromium installed successfully.")
    except Exception as e:
        print(f"❌ Error installing Playwright browsers: {e}")

def install_requirements():
    """Install pip requirements."""
    print("\n--- 🐍 Python Dependencies Stage ---")
    req_file = Path(__file__).parent / "requirements.txt"
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)], check=True)
        print("✅ Requirements installed successfully.")
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")

if __name__ == "__main__":
    print(f"🚀 Content Factory V2 Setup Starting (Root: {BASE_DIR})")
    install_requirements()
    setup_fonts()
    setup_playwright()
    print("\n🎉 Setup Complete!")
