import os
import sys
import time
import logging
from pathlib import Path

# Add paths
V2_ROOT = Path(__file__).parent.absolute()
PROJECT_ROOT = V2_ROOT.parent.absolute()

for p in [V2_ROOT, PROJECT_ROOT]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# 🛡️ Initialize Sentinel & Logging
from sentinel import Sentinel
sentinel = Sentinel()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(V2_ROOT / "error.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

from modules.text_renderer import ThaiTextRenderer
from modules.audio_generator import AudioGenerator
from modules.video_assembler import VideoAssembler
from modules.visual_generator import VisualGenerator

# Integration: Brain Module
from Core_Engine.Agents.writer import derivative_script_agent

def run_content_factory_full_production(topic: str):
    logging.info(f"--- 🚀 Content Factory V2: MASTER TRACK PRODUCTION (Topic: {topic}) ---")
    
    # 🔔 Report Start
    sentinel.report_start(topic)
    
    try:
        # 1. Input Context
        anchor_article = f"หัวข้อ: {topic}. เนื้อหาเจาะลึกที่น่าสนใจและมีประโยชน์สำหรับผู้ชม"
        tone = "ผู้เชี่ยวชาญ คุยง่าย ให้ความรู้เชิงลึก แต่ไม่ซีเรียสจนเกินไป"
        
        # 2. Brain Phase: Call Writer Agent
        logging.info("🖋️ Brain is thinking: Writing modular scene scripts...")
        scenes_data = derivative_script_agent(anchor_article, tone, client_dna="Money Insure Channel")
        
        if not isinstance(scenes_data, list):
            raise ValueError(f"Expected JSON Array from Writer Agent, got {type(scenes_data)}")

        temp_dir = V2_ROOT / "Temp_Production"
        os.makedirs(temp_dir, exist_ok=True)
        
        timestamp = int(time.time())
        final_output = V2_ROOT / "Test_Outputs" / f"Full_Production_{timestamp}.mp4"
        os.makedirs(final_output.parent, exist_ok=True)
        
        # 3. Initialize Engine Modules
        renderer = ThaiTextRenderer()
        audio_gen = AudioGenerator()
        visual_gen = VisualGenerator()
        assembler = VideoAssembler()
        
        # 🌟 4. MASTER AUDIO PHASE (Emotional Flow)
        master_audio_path, scenes_with_durations = audio_gen.generate_master_track(scenes_data, temp_dir)
        if not master_audio_path:
            raise RuntimeError("Master audio generation failed.")

        # 5. Visual Phase (Bake Images)
        processed_scenes = []
        for i, scene_timing in enumerate(scenes_with_durations):
            original_data = scenes_data[i]
            s_num = scene_timing["scene_number"]
            
            logging.info(f"📦 Baking Scene {s_num}: {original_data.get('graphic_header', '')[:20]}...")
            
            # A. Visual Generation (FAL.AI)
            bg_image_path = str(temp_dir / f"scene_{s_num}_bg.png")
            visual_prompt = original_data.get("visual_prompt", "Professional finance office background")
            visual_gen.generate_image(visual_prompt, bg_image_path)
            
            # B. Text Baking (Playwright)
            baked_img_path = str(temp_dir / f"scene_{s_num}_baked.png")
            renderer.render_scene(original_data["graphic_header"], bg_image_path, baked_img_path)
            
            processed_scenes.append({
                "baked_image": baked_img_path,
                "duration": scene_timing["duration"]
            })
            
        # 6. Assembly Phase (Build with BGM V2)
        output_path = assembler.assemble_video(processed_scenes, master_audio_path, str(final_output))
        
        if output_path and os.path.exists(output_path):
            logging.info(f"🎉 MASTER TRACK PRODUCTION SUCCESS! Final Video: {output_path}")
            # 🔔 Report Success
            sentinel.report_success(topic, output_path)
            return output_path
        else:
            raise RuntimeError("Video assembly failed or output file missing.")

    except Exception as e:
        logging.error(f"❌ Production Crash: {str(e)}", exc_info=True)
        # 🔔 Report Error
        sentinel.report_error(topic)
        return None

def parse_legacy_script(script_text: str) -> list:
    """
    🛠️ LIGACY BRIDGE:
    Converts V1 script [SCENE 1] format to V2 scene data list.
    """
    import re
    scenes = []
    # Find all [SCENE x] blocks
    # Pattern: [SCENE x] (Header if exists) \n Voice Text
    # Since V1 is loosely defined, we'll use a robust regex
    raw_blocks = re.split(r'\[SCENE\s*\d+\]', script_text)
    raw_blocks = [b.strip() for b in raw_blocks if b.strip()]
    
    for i, block in enumerate(raw_blocks):
        lines = block.split("\n")
        header = lines[0].strip() if lines else f"Scene {i+1}"
        voice = " ".join(lines[1:]).strip() if len(lines) > 1 else header
        
        scenes.append({
            "scene_number": i + 1,
            "voice_text": voice,
            "graphic_header": header,
            "visual_prompt": f"Professional cinematic shot matching: {header}, photorealistic, high resolution"
        })
    
    if not scenes:
        # Fallback if no [SCENE] tags found
        scenes.append({
            "scene_number": 1,
            "voice_text": script_text.strip(),
            "graphic_header": "Main Content",
            "visual_prompt": "Cinematic professional background, clean layout"
        })
    
    return scenes

def run_v2_engine_for_dashboard(job: dict, dna_payload: dict = None):
    """
    🔌 DASHBOARD ADAPTER (V2):
    This function is designed to be called directly from tab_04_delivery.py
    """
    topic = job.get("topic", "Untitled")
    logging.info(f"--- 🔌 V2 Engine Adapter: Starting for {topic} ---")
    
    # 🔔 Sentinel Start
    sentinel.report_start(topic)
    
    try:
        # 1. Parse Script (Bridge V1 to V2)
        script_raw = job.get("script", "")
        scenes_data = parse_legacy_script(script_raw)
        
        # 2. Setup Directories
        temp_dir = V2_ROOT / "Temp_Production"
        os.makedirs(temp_dir, exist_ok=True)
        
        timestamp = int(time.time())
        final_output = V2_ROOT / "Test_Outputs" / f"Dashboard_V2_{timestamp}.mp4"
        os.makedirs(final_output.parent, exist_ok=True)
        
        # 3. Initialize Modules
        renderer = ThaiTextRenderer()
        audio_gen = AudioGenerator()
        visual_gen = VisualGenerator()
        assembler = VideoAssembler()
        
        # 🌟 4. MASTER AUDIO (Master Track)
        master_audio_path, scenes_with_durations = audio_gen.generate_master_track(scenes_data, temp_dir)
        
        # 5. Visual Phase (Bake Images with Thai Vowel Fix)
        processed_scenes = []
        for i, scene_timing in enumerate(scenes_with_durations):
            original_data = scenes_data[i]
            s_num = scene_timing["scene_number"]
            
            # A. Visual
            bg_image_path = str(temp_dir / f"scene_{s_num}_bg.png")
            visual_gen.generate_image(original_data["visual_prompt"], bg_image_path)
            
            # B. Text Baking (Playwright) - THIS FIXES THE FLOATING VOWELS
            baked_img_path = str(temp_dir / f"scene_{s_num}_baked.png")
            renderer.render_scene(original_data["graphic_header"], bg_image_path, baked_img_path)
            
            processed_scenes.append({
                "baked_image": baked_img_path,
                "duration": scene_timing["duration"]
            })
            
        # 6. Final Assembly
        output_path = assembler.assemble_video(processed_scenes, master_audio_path, str(final_output))
        
        if output_path and os.path.exists(output_path):
            sentinel.report_success(topic, output_path)
            return output_path
        else:
            raise RuntimeError("V2 Output file missing after assembly.")
            
    except Exception as e:
        logging.error(f"❌ V2 Engine Failure: {str(e)}", exc_info=True)
        sentinel.report_error(topic)
        return None

if __name__ == "__main__":
    test_topic = "เคล็ดลับการออมเงินแบบคนยุคใหม่"
    run_content_factory_full_production(test_topic)
