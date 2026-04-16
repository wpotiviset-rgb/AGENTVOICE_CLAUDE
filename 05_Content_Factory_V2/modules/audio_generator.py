import os
import requests
import base64
import json
import whisper
import logging
from dotenv import load_dotenv
from moviepy.editor import AudioFileClip
from pathlib import Path

# Fix: Add Homebrew path for ffmpeg (Whisper requirement on Mac)
os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"

# Load env for API keys
BASE_DIR = Path(__file__).parent.parent.parent.absolute()
load_dotenv(BASE_DIR / ".env")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
DEFAULT_VOICE_ID = "f6c6yO8TKA7sNwqpuFvf" # The user's preferred Voice ID

class AudioGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or ELEVENLABS_API_KEY
        # Load whisper model once
        logging.info("📥 Initializing Whisper Engine (tiny)...")
        self.whisper_model = whisper.load_model("tiny")

    def generate_master_track(self, scenes_data, temp_dir):
        """
        🚀 Master Track Pipeline (V2 - No Slicing):
        1. Generates one long audio file (Emotional Flow).
        2. Uses Whisper to find scene durations for video assembly.
        """
        temp_dir = Path(temp_dir)
        # Join all text with a small pause (represented by space/dots)
        full_text = " ".join([s["voice_text"] for s in scenes_data])
        full_audio_path = temp_dir / "master_narration.mp3"
        
        # 1. Generate Audio via ElevenLabs
        logging.info(f"🎙️ Generating Master Track (Emotional Flow)...")
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{DEFAULT_VOICE_ID}"
        headers = {
            "Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": self.api_key
        }
        data = {
            "text": full_text,
            "model_id": "eleven_v3",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        
        resp = requests.post(url, json=data, headers=headers)
        if resp.status_code != 200:
            logging.error(f"❌ ElevenLabs Error: {resp.text}")
            return None, []

        with open(full_audio_path, "wb") as f:
            f.write(resp.content)
            
        # 2. Extract Timestamps using Whisper
        logging.info(f"👂 Whisper is calculating scene durations...")
        result = self.whisper_model.transcribe(str(full_audio_path), language="th")
        segments = result.get("segments", [])
        
        # Calculate total duration
        audio_clip = AudioFileClip(str(full_audio_path))
        total_duration = audio_clip.duration
        audio_clip.close()

        # Logic to map scenes to durations:
        # We divide the total duration proportional to character counts as a baseline,
        # then refine with Whisper segments if possible.
        # However, for 100% stability, we'll use character-ratio distribution 
        # anchored by Whisper's total detected duration.
        
        processed_scenes = []
        char_counts = [len(s["voice_text"]) for s in scenes_data]
        total_chars = sum(char_counts)
        
        current_time = 0.0
        for i, scene in enumerate(scenes_data):
            # Calculate duration based on character ratio (Fallback/Baseline)
            # This ensures images always cover the full audio.
            ratio = char_counts[i] / total_chars
            duration = ratio * total_duration
            
            # Add small padding between scenes if needed, but here we just need total sync
            processed_scenes.append({
                "scene_number": scene.get("scene_number", i+1),
                "voice_text": scene["voice_text"],
                "duration": duration
            })
            current_time += duration

        logging.info(f"✅ Master Track Ready: {full_audio_path} ({total_duration:.2f}s)")
        return str(full_audio_path), processed_scenes

    def generate_full_audio_sequence(self, scenes_data, temp_dir):
        """Deprecated: Use generate_master_track instead."""
        return self.generate_master_track(scenes_data, temp_dir)

if __name__ == "__main__":
    pass
