import os
import time
import logging
from datetime import datetime
from pathlib import Path
from Core_Engine.notification_manager import send_telegram_notify
from Core_Engine.model_router import call_llm

# Config
V2_ROOT = Path(__file__).parent.absolute()
ERROR_LOG_PATH = V2_ROOT / "error.log"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB

class Sentinel:
    def __init__(self):
        self.start_time = None
        self._check_log_size()

    def _check_log_size(self):
        """🛡️ Rotate log if it exceeds MAX_LOG_SIZE"""
        if ERROR_LOG_PATH.exists() and ERROR_LOG_PATH.stat().st_size > MAX_LOG_SIZE:
            print(f"🧹 Sentinel: Log exceeded 5MB. Rotating...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ERROR_LOG_PATH.rename(V2_ROOT / f"error_{timestamp}.log")

    def report_start(self, topic: str):
        """🚀 Notify boss that production has started"""
        self.start_time = time.time()
        msg = (
            f"<b>🚀 Content Factory V2 เริ่มเดินเครื่องแล้ว!</b>\n\n"
            f"🎯 <b>กำลังผลิตหัวข้อ:</b> {topic}\n"
            f"⌚ <i>เวลาเริ่ม: {datetime.now().strftime('%H:%M:%S')}</i>"
        )
        send_telegram_notify(msg)

    def report_success(self, topic: str, output_path: str):
        """✅ Notify boss that production finished successfully"""
        duration_sec = time.time() - self.start_time
        duration_min = duration_sec / 60
        
        msg = (
            f"<b>✅ ผลิตวิดีโอสำเร็จ!</b>\n\n"
            f"🎯 <b>หัวข้อ:</b> {topic}\n"
            f"⏱️ <b>ใช้เวลาผลิตรวม:</b> {duration_min:.2f} นาที\n"
            f"📂 <b>ไฟล์อยู่ที่:</b> <code>{output_path}</code>"
        )
        send_telegram_notify(msg)

    def report_error(self, topic: str):
        """⚠️ Analyze log and notify boss about the error with AI summary"""
        print("🚨 Sentinel: Detected error. Analyzing logs...")
        
        # 1. Read last 5 lines from error.log
        error_context = ""
        if ERROR_LOG_PATH.exists():
            with open(ERROR_LOG_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()
                error_context = "".join(lines[-10:]) # Read 10 to be safe, AI will summarize

        # 2. Call AI to summarize
        summary = self._summarize_error_ai(error_context)
        
        msg = (
            f"<b>⚠️ Content Factory V2 ตรวจพบปัญหา!</b>\n\n"
            f"❌ <b>หัวข้อ:</b> {topic}\n"
            f"🧠 <b>AI สรุปสาเหตุ:</b>\n<i>{summary}</i>\n\n"
            f"🔍 <i>บอสลองเช็ค error.log ดูอีกทีนะครับ</i>"
        )
        send_telegram_notify(msg)

    def _summarize_error_ai(self, log_context: str) -> str:
        """🧠 Use AI to summarize the error log in friendly Thai"""
        if not log_context:
            return "ไม่พบข้อมูลใน Log ครับบอส แต่น่าจะมีอะไรบางอย่างค้าง"

        prompt = (
            "คุณคือ 'Sentinel' ยามเฝ้าระบบ AI Content Factory.\n"
            "ข้อมูลข้างล่างคือ Error Logs ล่าสุดที่เพิ่งเกิดขึ้น.\n"
            "หน้าที่: สรุปสาเหตุที่พังเป็น 'ภาษาไทย' แบบสั้นๆ กระชับ และเป็นกันเอง (บอกตรงๆ ว่าอะไรพัง และต้องแก้ที่จุดไหน).\n"
            "ห้ามตอบยาว ห้ามมีคำนำเกริ่นเยอะ เอาเนื้อๆ.\n\n"
            f"LOG CONTEXT:\n{log_context}"
        )
        
        try:
            messages = [{"role": "system", "content": prompt}]
            summary = call_llm(messages, temperature=0.5)
            return summary.strip()
        except Exception as e:
            return f"AI สรุปไม่ได้ครับ (Error: {e}) แต่ดูเหมือนจะมีปัญหาที่ Log ท้ายไฟล์ครับ"

if __name__ == "__main__":
    # Test
    s = Sentinel()
    # s.report_start("ทดสอบระบบ Sentinel")
    # s.report_error("ทดสอบระบบ Sentinel")
