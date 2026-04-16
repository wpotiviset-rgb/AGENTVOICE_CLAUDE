import os
import sys
from pathlib import Path

# Add project modules to path
V2_ROOT = Path(__file__).parent.absolute()
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from modules.text_renderer import ThaiTextRenderer

def run_font_test():
    print("--- 🧐 Verifying Thai Font Rendering Accuracy ---")
    
    # 1. Initialize Renderer
    renderer = ThaiTextRenderer()
    
    # 2. Setup Paths
    base_dir = Path(__file__).parent.parent.absolute()
    assets_dir = base_dir / "Assets"
    output_dir = V2_ROOT / "Test_Outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Use any existing image as background for test
    bg_path = assets_dir / "AI_Agent_Icon.png"
    if not bg_path.exists():
        # Create a dummy colored background if missing
        from PIL import Image
        img = Image.new('RGB', (1080, 1920), color = (73, 109, 137))
        bg_path = output_dir / "dummy_bg.png"
        img.save(bg_path)
    
    test_file = output_dir / "Font_Verification_Test.png"
    
    # 3. Render Sample
    test_text = "เรื่องจริงที่หลายคนไม่รู้! สระลอยมั้ยแฮะ? 🚀 ชั้น 3+ เคลมได้ 2 ที่"
    renderer.render_scene(test_text, str(bg_path), str(test_file))
    
    if test_file.exists():
        print(f"\n✅ SUCCESS: Font test image generated at:\n{test_file}")
        print("Please check this file to verify Thai typography accuracy.")
    else:
        print("\n❌ ERROR: Failed to generate test image.")

if __name__ == "__main__":
    run_font_test()
