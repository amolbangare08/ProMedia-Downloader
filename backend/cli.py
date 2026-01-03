import argparse
import json
import sys
import os

# Ensure we can import from the same directory
sys.path.append(os.path.dirname(__file__))

from core import *
from downloaders import DownloaderMixin

class HeadlessDownloader(DownloaderMixin):
    def __init__(self):
        # 1. Mock the Stop Event
        self.stop_event = type('obj', (object,), {'is_set': lambda: False})
        
        # 2. Setup Paths (Same as before)
        self.ffmpeg_path = "./ffmpeg.exe" if os.path.exists("./ffmpeg.exe") else "ffmpeg"
        self.handbrake_path = "./HandBrakeCLI.exe" if os.path.exists("./HandBrakeCLI.exe") else "HandBrakeCLI"
        
        if not os.path.exists(self.ffmpeg_path):
             local_ff = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
             if os.path.exists(local_ff): self.ffmpeg_path = local_ff

        if not os.path.exists(self.handbrake_path):
             local_hb = os.path.join(os.path.dirname(__file__), "HandBrakeCLI.exe")
             if os.path.exists(local_hb): self.handbrake_path = local_hb

    # --- THE SMART MOCKS ---
    # These classes trick 'downloaders.py' into thinking it's updating a UI,
    # but actually, they print JSON to the console for Electron to read.

    class MockProgressBar:
        def __init__(self):
            self._val = 0.0
        
        def set(self, val):
            self._val = float(val)
            # THE FIX: Print JSON whenever progress changes!
            # This sends the update to Electron immediately.
            print(json.dumps({"type": "progress", "data": self._val}), flush=True)

        def get(self):
            return self._val
        
        # Dummy methods to prevent crashes
        def configure(self, **kwargs): pass
        def start(self): pass
        def stop(self): pass

    class MockStatusVar:
        def __init__(self, progress_bar_ref):
            self.pb = progress_bar_ref

        def set(self, val):
            # When Python sets status text (e.g. "Processing..."), sends it to Electron
            # We attach the current progress value so the bar doesn't jump to 0
            print(json.dumps({
                "type": "progress", 
                "data": self.pb.get(), 
                "text": str(val)
            }), flush=True)

    # --- UI COMPATIBILITY ---
    # These dummy methods prevent crashes when downloaders.py tries to update buttons
    def after(self, delay, func): 
        func() # Run immediately

    def emit_status(self, type, data):
        print(json.dumps({"type": type, "data": data}), flush=True)

    def finish_success(self):
        self.emit_status("success", "Download Complete")
    
    def finish_fail(self, message):
        self.emit_status("error", message)

    # --- MAIN RUNNER ---
    def run_headless(self, args):
        # 1. Initialize Smart Mocks
        self.progress_bar = self.MockProgressBar()
        self.status_var = self.MockStatusVar(self.progress_bar)
        
        # 2. Mock other UI elements referenced in downloaders.py (Passive mocks)
        self.status_label = type('obj', (object,), {'configure': lambda **k: None})
        self.download_btn = type('obj', (object,), {'configure': lambda **k: None})
        self.format_switch = type('obj', (object,), {'configure': lambda **k: None})
        self.res_menu = type('obj', (object,), {'configure': lambda **k: None})
        self.hb_checkbox = type('obj', (object,), {'configure': lambda **k: None})
        self.trim_checkbox = type('obj', (object,), {'configure': lambda **k: None})
        self.audio_fmt_menu = type('obj', (object,), {'configure': lambda **k: None})
        
        # 3. Run the shared logic from downloaders.py
        self.run_download_manager(
            url=args.url,
            folder=args.folder,
            mode=args.mode,
            res=args.res,
            audio_fmt=args.audio_fmt,
            use_hb=args.use_hb,
            hb_preset=args.hb_preset,
            trim_on=args.trim_on,
            t_start=args.trim_start,
            t_end=args.trim_end
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--folder", required=True)
    parser.add_argument("--mode", default="Video + Audio")
    parser.add_argument("--res", default="Best Available")
    parser.add_argument("--audio_fmt", default="mp3")
    parser.add_argument("--use_hb", action="store_true")
    parser.add_argument("--hb_preset", default="Auto (Smart Match)")
    parser.add_argument("--trim_on", action="store_true")
    parser.add_argument("--trim_start", default="")
    parser.add_argument("--trim_end", default="")

    args = parser.parse_args()
    
    try:
        app = HeadlessDownloader()
        app.run_headless(args)
    except Exception as e:
        print(json.dumps({"type": "error", "data": str(e)}), flush=True)