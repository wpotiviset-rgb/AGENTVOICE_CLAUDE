import os
import random
import logging
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip, afx
from pathlib import Path

# Path Config
BASE_DIR = Path(__file__).parent.parent.parent.absolute()
BGM_DIR = BASE_DIR / "Assets" / "BGM"

class VideoAssembler:
    def __init__(self):
        # Ensure BGM dir exists
        os.makedirs(BGM_DIR, exist_ok=True)

    def _get_random_bgm(self):
        """
        🚀 BGM Guardrail (V2):
        1. Ignore files containing 'test'.
        2. Ignore files shorter than 10 seconds (likely junk/voice clips).
        """
        try:
            if not os.path.exists(BGM_DIR):
                return None
            bgm_files = [f for f in os.listdir(BGM_DIR) if f.endswith(".mp3")]
            
            # Filter 1: Naming Guardrail
            valid_files = [f for f in bgm_files if "test" not in f.lower()]
            
            if not valid_files:
                return None
            
            # Filter 2: Duration Guardrail
            random.shuffle(valid_files) # Shuffle to pick randomly but still validate
            for f_name in valid_files:
                f_path = str(BGM_DIR / f_name)
                try:
                    clip = AudioFileClip(f_path)
                    duration = clip.duration
                    clip.close()
                    
                    if duration >= 10:
                        return f_path
                    else:
                        logging.info(f"⚠️ Skipping BGM '{f_name}': Too short ({duration:.1f}s).")
                except Exception as e:
                    logging.error(f"⚠️ Could not read BGM '{f_name}': {e}")
                    continue
            
            return None
        except Exception as e:
            logging.error(f"⚠️ BGM Scanner Error: {e}")
            return None

    def assemble_video(self, processed_scenes, master_audio_path, output_path):
        """
        🚀 Master Track Assembly (V2):
        1. Concatenates image clips based on whisper-calculated durations.
        2. Overlays the single Master Voice Track.
        3. Mixes in BGM (0.08 vol) with 2s fade-out.
        """
        logging.info(f"🎬 Starting Master Track Assembly ({len(processed_scenes)} scenes)...")
        
        clips = []
        for scene in processed_scenes:
            # 1. Create Image Clip from baked image
            # The duration is now controlled by the Master Track alignment
            img_clip = ImageClip(scene["baked_image"]).set_duration(scene["duration"])
            clips.append(img_clip)
            
        # 2. Concatenate all visuals
        final_video = concatenate_videoclips(clips, method="compose")
        v_duration = final_video.duration
        
        # 3. Master Voice Track Overlay
        logging.info(f"🎙️ Overlaying Master Voice Track...")
        master_voice = AudioFileClip(master_audio_path)
        # Ensure audio matches video duration (trim if necessary, though they should match)
        master_voice = master_voice.subclip(0, min(master_voice.duration, v_duration))
        
        # 🛡️ 4. BGM TRACK PIPELINE (V2)
        bgm_path = self._get_random_bgm()
        final_audio = master_voice
        
        if bgm_path:
            logging.info(f"🎶 Mixing BGM: {os.path.basename(bgm_path)}...")
            try:
                # Load BGM
                bgm_clip = AudioFileClip(bgm_path)
                
                # Logic: Loop if shorter than video
                if bgm_clip.duration < v_duration:
                    bgm_clip = afx.audio_loop(bgm_clip, duration=v_duration)
                else:
                    bgm_clip = bgm_clip.subclip(0, v_duration)
                
                # Logic: Volume Ducking (0.08 as per requirement)
                bgm_clip = bgm_clip.volumex(0.08)
                
                # Logic: Professional Fade-out (2 seconds)
                bgm_clip = bgm_clip.audio_fadeout(2)
                
                # Mix Voice + BGM
                final_audio = CompositeAudioClip([master_voice, bgm_clip])
                
            except Exception as e:
                logging.error(f"⚠️ BGM Mix Error (Safeguard Triggered): {e}")
                # Fallback: final_audio remains master_voice

        # Set final mixed audio to video
        final_video = final_video.set_audio(final_audio)

        # 5. Write to file
        logging.info(f"💾 Exporting Master Track Video: {output_path}")
        final_video.write_videofile(
            output_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            audio_bitrate="192k",
            audio_fps=44100,
            preset="ultrafast",
            threads=4,
            logger=None
        )
        
        # Cleanup
        final_video.close()
        master_voice.close()
        return output_path

if __name__ == "__main__":
    pass
