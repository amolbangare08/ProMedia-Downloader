import os
import sys
import subprocess
import time
import zipfile
import shutil
import ctypes
import threading
import re
import socket
import random
import glob
import tkinter as tk
import winreg 
from tkinter import filedialog

# --- 1. BOOTSTRAP LIBRARIES ---
def is_frozen():
    return getattr(sys, 'frozen', False)

if not is_frozen():
    required = ["customtkinter", "yt_dlp", "requests"]
    for lib in required:
        try:
            module_name = lib.replace("-", "_") 
            __import__(module_name)
        except ImportError:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            except:
                print(f"[Error] Failed to install {lib}.")

# --- 2. IMPORTS ---
import requests
import customtkinter as ctk
import yt_dlp

# --- 3. SYSTEM ACCENT COLOR ---
def get_windows_accent():
    try:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\DWM")
        value, type = winreg.QueryValueEx(key, "ColorizationColor")
        return f"#{hex(value)[4:]}"
    except:
        return "#6366f1"

# --- 4. ADAPTIVE COLOR PALETTE (Light, Dark) ---
C_BG           = ("#ffffff", "#09090b") 
C_CARD         = ("#f4f4f5", "#18181b") 
C_CARD_BORDER  = ("#e4e4e7", "#27272a") 

C_TEXT_MAIN    = ("#18181b", "#fafafa") 
C_TEXT_SUB     = ("#71717a", "#a1a1aa") 

C_INPUT_BG     = ("#ffffff", "#09090b")
C_INPUT_BORDER = ("#d4d4d8", "#3f3f46") 

# Specific fix for Segmented Button Text visibility
# We make unselected background darker in light mode so White text always works
C_SEGMENT_UNSELECTED = ("#a1a1aa", "#27272a") 
C_SEGMENT_TEXT       = "#ffffff" # Always white for best contrast on Accents

SYS_ACCENT     = get_windows_accent()
C_ACCENT       = ("#4f46e5", "#6366f1") 
C_ACCENT_HOVER = ("#4338ca", "#4f46e5") 

C_STOP         = ("#ef4444", "#ef4444") 
C_STOP_HOVER   = ("#dc2626", "#dc2626")
C_SUCCESS      = ("#10b981", "#10b981") 
C_ERROR        = ("#ef4444", "#ef4444") 

YOUTUBE_REGEX = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
HANDBRAKE_URL = "https://github.com/HandBrake/HandBrake/releases/download/1.8.2/HandBrakeCLI-1.8.2-win-x86_64.zip"

# --- PROXY LOADING ---
def load_proxies():
    proxy_file = "proxies.txt"
    if os.path.exists(proxy_file):
        try:
            with open(proxy_file, "r") as f:
                return [line.strip() for line in f if line.strip()]
        except: return []
    return []

PROXY_POOL = load_proxies()

# --- HELPER FUNCTIONS ---
def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def hide_console():
    if sys.platform == 'win32':
        kernel32 = ctypes.WinDLL('kernel32')
        user32 = ctypes.WinDLL('user32')
        hWnd = kernel32.GetConsoleWindow()
        if hWnd: user32.ShowWindow(hWnd, 0)

def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError: return False

def check_tool_dependencies():
    print("-" * 50); print("SYSTEM INITIALIZATION..."); print("-" * 50)
    cwd = os.getcwd()
    ffmpeg_path = os.path.join(cwd, "ffmpeg.exe")
    handbrake_path = os.path.join(cwd, "HandBrakeCLI.exe")

    if not os.path.exists(ffmpeg_path):
        if shutil.which("ffmpeg"): ffmpeg_path = shutil.which("ffmpeg")
        else:
            try:
                r = requests.get(FFMPEG_URL, stream=True, proxies={"http": None, "https": None})
                if r.status_code == 200:
                    with open("ffmpeg.zip", 'wb') as f: shutil.copyfileobj(r.raw, f)
                    with zipfile.ZipFile("ffmpeg.zip", 'r') as z:
                        for i in z.infolist():
                            if i.filename.endswith("bin/ffmpeg.exe"):
                                i.filename = "ffmpeg.exe"; z.extract(i, cwd); break
                    os.remove("ffmpeg.zip")
            except: pass

    if not os.path.exists(handbrake_path):
        try:
            h = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(HANDBRAKE_URL, headers=h, stream=True, proxies={"http": None, "https": None})
            if r.status_code == 200:
                with open("handbrake.zip", 'wb') as f: shutil.copyfileobj(r.raw, f)
                with zipfile.ZipFile("handbrake.zip", 'r') as z:
                    for i in z.infolist():
                        if i.filename.endswith("HandBrakeCLI.exe"):
                            i.filename = "HandBrakeCLI.exe"; z.extract(i, cwd); break
                os.remove("handbrake.zip")
        except: pass

    return ffmpeg_path, handbrake_path

# --- TOOLTIP ---
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text: return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#27272a", foreground="#fafafa",
                         relief="flat", borderwidth=0, font=("Segoe UI", 9), padx=8, pady=6)
        label.pack()

    def hide_tip(self, event=None):
        if self.tipwindow: self.tipwindow.destroy(); self.tipwindow = None

# --- MAIN UI ---
class ModernDownloaderApp(ctk.CTk):
    def __init__(self, ffmpeg_path, handbrake_path):
        super().__init__()
        self.ffmpeg_path = ffmpeg_path
        self.handbrake_path = handbrake_path
        self.stop_event = threading.Event()
        self.current_process = None
        
        icon_path = resource_path("app.ico")
        if os.path.exists(icon_path): self.iconbitmap(icon_path)
        self.title("ProMedia Downloader")
        self.geometry("800x600")
        self.resizable(True, True) 
        ctk.set_appearance_mode("Dark")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.configure(fg_color=C_BG)

        self.url_var = ctk.StringVar()
        self.status_var = ctk.StringVar(value="")
        self.current_accent = C_ACCENT
        self.current_accent_hover = C_ACCENT_HOVER

        # --- 1. TOP BAR ---
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 0))
        
        self.theme_menu = ctk.CTkOptionMenu(
            self.top_bar, values=["Light", "Dark", "System"], command=self.change_theme,
            width=90, height=28, font=("Segoe UI", 11), fg_color=C_CARD_BORDER,
            text_color=C_TEXT_MAIN, button_color=C_INPUT_BORDER, button_hover_color=C_TEXT_SUB
        )
        self.theme_menu.pack(side="right")
        ctk.CTkLabel(self.top_bar, text="Theme:", font=("Segoe UI", 11), text_color=C_TEXT_SUB).pack(side="right", padx=5)

        self.accent_menu = ctk.CTkOptionMenu(
            self.top_bar, values=["Indigo", "Windows System", "Emerald", "Blue"], command=self.change_accent,
            width=130, height=28, font=("Segoe UI", 11), fg_color=C_CARD_BORDER,
            text_color=C_TEXT_MAIN, button_color=C_INPUT_BORDER, button_hover_color=C_TEXT_SUB
        )
        self.accent_menu.pack(side="right", padx=(0, 20))
        ctk.CTkLabel(self.top_bar, text="Accent:", font=("Segoe UI", 11), text_color=C_TEXT_SUB).pack(side="right", padx=5)

        # --- 2. MAIN CONTENT ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self.card = ctk.CTkFrame(self.main_container, corner_radius=24, fg_color=C_CARD, border_width=1, border_color=C_CARD_BORDER)
        self.card.grid(row=0, column=0, sticky="ew")

        # Header
        self.title_label = ctk.CTkLabel(self.card, text="YT DOWNLOADER", font=("Segoe UI", 24, "bold"), text_color=C_TEXT_MAIN)
        self.title_label.pack(pady=(40, 5))
        self.subtitle_label = ctk.CTkLabel(self.card, text="Professional Video & Audio Extractor", font=("Segoe UI", 12), text_color=C_TEXT_SUB)
        self.subtitle_label.pack(pady=(0, 30))

        # Input
        self.input_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=50)
        
        self.url_entry = ctk.CTkEntry(
            self.input_frame, textvariable=self.url_var, placeholder_text="Paste YouTube link here...", height=50,
            font=("Segoe UI", 13), border_width=1, border_color=C_INPUT_BORDER, fg_color=C_INPUT_BG, text_color=C_TEXT_MAIN, corner_radius=12
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.url_entry.bind("<KeyRelease>", self.clear_status)

        self.paste_btn = ctk.CTkButton(
            self.input_frame, text="PASTE", width=100, height=50, font=("Segoe UI", 12, "bold"),
            fg_color=self.current_accent, hover_color=self.current_accent_hover, text_color="#ffffff", corner_radius=12,
            command=self.paste_clipboard
        )
        self.paste_btn.pack(side="right")

        # Controls
        self.controls_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.controls_frame.pack(pady=25, padx=50, fill="x")

        self.format_var = ctk.StringVar(value="Video + Audio")
        # FIXED: Unselected color is slightly darker in light mode so White text works
        self.format_switch = ctk.CTkSegmentedButton(
            self.controls_frame, values=["Video + Audio", "Video Only", "Audio Only"], variable=self.format_var,
            font=("Segoe UI", 12, "bold"), height=40, corner_radius=10,
            selected_color=self.current_accent, selected_hover_color=self.current_accent_hover,
            unselected_color=C_SEGMENT_UNSELECTED, unselected_hover_color=C_INPUT_BORDER, 
            text_color=C_SEGMENT_TEXT, # Forced White Text
            command=self.update_options_visibility 
        )
        self.format_switch.pack(fill="x", pady=(0, 15))

        self.options_container = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.options_container.pack(fill="x")

        # Options
        self.res_var = ctk.StringVar(value="Best Available")
        self.res_menu = ctk.CTkOptionMenu(
            self.options_container, values=["Best Available", "2160p (4K)", "1440p (2K)", "1080p", "720p", "480p"], variable=self.res_var,
            width=140, height=35, fg_color=C_INPUT_BG, button_color=C_INPUT_BORDER, button_hover_color=C_CARD_BORDER,
            text_color=C_TEXT_MAIN, font=("Segoe UI", 12), dropdown_fg_color=C_CARD, dropdown_text_color=C_TEXT_MAIN
        )

        self.use_hb_var = ctk.BooleanVar(value=True)
        self.hb_checkbox = ctk.CTkCheckBox(
            self.options_container, text="Optimize (HandBrake)", variable=self.use_hb_var,
            font=("Segoe UI", 12), text_color=C_TEXT_MAIN, border_color=C_TEXT_SUB,
            hover_color=self.current_accent, fg_color=self.current_accent, checkmark_color="white",
            command=self.toggle_hb_menu
        )
        ToolTip(self.hb_checkbox, "Professional re-encoding for Premiere Pro compatibility.")

        self.hb_preset_var = ctk.StringVar(value="Auto (Smart Match)")
        self.hb_menu = ctk.CTkOptionMenu(
            self.options_container,
            values=["Auto (Smart Match)", "Fast 1080p30", "HQ 1080p30 Surround", "Fast 2160p60 4K", "HQ 2160p60 4K", "Fast 720p30", "Production Standard"],
            variable=self.hb_preset_var, width=180, height=35, fg_color=C_INPUT_BG, button_color=C_INPUT_BORDER,
            button_hover_color=C_CARD_BORDER, text_color=C_TEXT_MAIN, font=("Segoe UI", 12), dropdown_fg_color=C_CARD
        )

        self.audio_fmt_var = ctk.StringVar(value="mp3")
        self.audio_fmt_menu = ctk.CTkOptionMenu(
            self.options_container, values=["mp3", "m4a", "wav", "flac"], variable=self.audio_fmt_var,
            width=100, height=35, fg_color=C_INPUT_BG, button_color=C_INPUT_BORDER, text_color=C_TEXT_MAIN
        )
        self.update_options_visibility("Video + Audio")

        # Action Area
        self.action_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.action_frame.pack(pady=(10, 30), padx=50, fill="x", side="bottom")

        self.status_label = ctk.CTkLabel(self.action_frame, textvariable=self.status_var, text_color=C_TEXT_SUB, font=("Segoe UI", 11))
        self.status_label.pack(side="bottom", pady=(5, 0))

        self.progress_bar = ctk.CTkProgressBar(self.action_frame, height=6, corner_radius=3, progress_color=self.current_accent, fg_color=C_INPUT_BORDER)
        self.progress_bar.set(0)

        self.download_btn = ctk.CTkButton(
            self.action_frame, text="START DOWNLOAD", font=("Segoe UI", 13, "bold"), height=55, corner_radius=12,
            fg_color=self.current_accent, hover_color=self.current_accent_hover, text_color="#ffffff",
            command=self.initiate_download
        )
        self.download_btn.pack(fill="x", pady=(0, 15))

    # --- THEMING ENGINE ---
    def change_theme(self, mode): ctk.set_appearance_mode(mode)

    def change_accent(self, color_name):
        if color_name == "Windows System": sys_col = SYS_ACCENT; self.current_accent = (sys_col, sys_col); self.current_accent_hover = (sys_col, sys_col)
        elif color_name == "Emerald": self.current_accent = ("#10b981", "#10b981"); self.current_accent_hover = ("#059669", "#059669")
        elif color_name == "Blue": self.current_accent = ("#3b82f6", "#3b82f6"); self.current_accent_hover = ("#2563eb", "#2563eb")
        else: self.current_accent = ("#4f46e5", "#6366f1"); self.current_accent_hover = ("#4338ca", "#4f46e5")
        
        self.download_btn.configure(fg_color=self.current_accent, hover_color=self.current_accent_hover)
        self.paste_btn.configure(fg_color=self.current_accent, hover_color=self.current_accent_hover)
        self.format_switch.configure(selected_color=self.current_accent, selected_hover_color=self.current_accent_hover)
        self.hb_checkbox.configure(hover_color=self.current_accent, fg_color=self.current_accent)
        self.progress_bar.configure(progress_color=self.current_accent)

    # --- UI LOGIC ---
    def toggle_hb_menu(self):
        state = "normal" if self.use_hb_var.get() else "disabled"
        self.hb_menu.configure(state=state)

    def update_options_visibility(self, choice):
        for w in self.options_container.winfo_children(): w.pack_forget()
        if choice == "Audio Only": self.audio_fmt_menu.pack(side="left")
        else: self.res_menu.pack(side="left", padx=(0, 15)); self.hb_checkbox.pack(side="left", padx=(0, 10)); self.hb_menu.pack(side="left")

    def clear_status(self, event=None):
        if not self.downloading: self.status_var.set(""); self.status_label.configure(text_color=C_TEXT_SUB)

    def clear_status_completely(self):
        if not self.downloading: self.status_var.set(""); self.progress_bar.pack_forget()

    def paste_clipboard(self):
        try: self.url_var.set(self.clipboard_get()); self.clear_status() 
        except: pass

    # --- PROCESS LOGIC ---
    def stop_process(self):
        if self.downloading:
            self.status_var.set("Stopping...")
            self.stop_event.set()
            if self.current_process:
                try: self.current_process.kill()
                except: pass
            self.downloading = False
            self.download_btn.configure(text="START DOWNLOAD", fg_color=self.current_accent, hover_color=self.current_accent_hover, command=self.initiate_download)
            self.status_var.set("Stopped by user"); self.status_label.configure(text_color=C_STOP)
            self.progress_bar.configure(progress_color=C_STOP)

    def initiate_download(self):
        if self.downloading: return
        self.status_var.set("Initializing...")
        self.status_label.configure(text_color=C_TEXT_SUB)
        self.progress_bar.configure(progress_color=self.current_accent)
        self.stop_event.clear()
        
        url = self.url_var.get().strip()
        if not re.match(YOUTUBE_REGEX, url): self.finish_fail("Please enter a valid YouTube URL"); return
        if not check_internet(): self.finish_fail("Internet connection required"); return

        folder = filedialog.askdirectory()
        if not folder: self.status_var.set(""); return

        self.downloading = True
        self.download_btn.configure(text="STOP DOWNLOAD", fg_color=C_STOP, hover_color=C_STOP_HOVER, command=self.stop_process)
        self.progress_bar.pack(fill="x", pady=(0, 10), before=self.status_label)
        self.progress_bar.set(0)
        
        self.format_switch.configure(state="disabled"); self.res_menu.configure(state="disabled"); self.hb_checkbox.configure(state="disabled"); self.hb_menu.configure(state="disabled"); self.audio_fmt_menu.configure(state="disabled")
        
        threading.Thread(target=self.run_download_manager, args=(url, folder, self.format_var.get(), self.res_var.get(), self.audio_fmt_var.get(), self.use_hb_var.get(), self.hb_preset_var.get()), daemon=True).start()

    def run_download_manager(self, url, folder, mode, res, audio_fmt, use_hb, hb_preset):
        print("Attempting Direct Connection...")
        status = self.run_download_task(url, folder, mode, res, audio_fmt, use_hb, hb_preset, proxy=None)
        
        if self.stop_event.is_set() or status == 0 or status == 2: return 

        self.status_var.set("Network blocked. Switching to Proxies...")
        print("Engaging Proxies...")
        
        max_retries = 5; used_proxies = set()
        for i in range(max_retries):
            if self.stop_event.is_set(): return
            available = [p for p in PROXY_POOL if p not in used_proxies]
            if not available: break 
            proxy_url = f"http://{random.choice(available)}"
            self.status_var.set(f"Retrying with Secure Proxy ({i+1}/{max_retries})...")
            status = self.run_download_task(url, folder, mode, res, audio_fmt, use_hb, hb_preset, proxy=proxy_url)
            if status == 0 or status == 2: return 
            time.sleep(1)

        if not self.stop_event.is_set(): self.finish_fail("Connection failed. Try again later.")

    def run_download_task(self, url, folder, mode, res_text, audio_fmt, use_hb, hb_preset, proxy):
        temp_filename = f"temp_{int(time.time())}"
        def progress_hook(d):
            if self.stop_event.is_set(): raise Exception("Stopped")
            if d["status"] == "downloading" and d.get("total_bytes"):
                self.progress_bar.set(d["downloaded_bytes"] / d["total_bytes"])
                self.status_var.set(f"Downloading Source: {int(self.progress_bar.get() * 100)}%")

        height_limit = None
        if "Best" not in res_text:
            try: height_limit = int(res_text.split("p")[0])
            except: pass

        ydl_opts = {
            "outtmpl": os.path.join(folder, f"{temp_filename}.%(ext)s"),
            "progress_hooks": [progress_hook], "quiet": True, "noplaylist": True, "socket_timeout": 20, "retries": 3,
            "ffmpeg_location": self.ffmpeg_path
        }
        if proxy: ydl_opts["proxy"] = proxy

        if mode == "Audio Only":
            ydl_opts.update({
                "format": "bestaudio/best", "outtmpl": os.path.join(folder, f"%(title)s.{audio_fmt}"),
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": audio_fmt}],
            })
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url])
                self.after(0, self.finish_success); return 0
            except Exception as e: return 2 if "Stopped" in str(e) else 1

        if height_limit: ydl_opts["format"] = f"bestvideo[height<={height_limit}]+bestaudio/best[height<={height_limit}]/best"
        else: ydl_opts["format"] = "bestvideo+bestaudio/best"
        ydl_opts["merge_output_format"] = "mkv"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                final_title = re.sub(r'[\\/*?:"<>|]', "", info.get('title', 'video'))
                video_height = info.get('height', 0) or (height_limit if height_limit else 1080)
                video_width = info.get('width', 0) or 1920
            
            temp_files = glob.glob(os.path.join(folder, f"{temp_filename}.*"))
            if not temp_files: raise Exception("Temp missing")
            temp_fullpath = temp_files[0]
            ext = os.path.splitext(temp_fullpath)[1]
            final_output = os.path.join(folder, f"{final_title}.mp4" if use_hb else f"{final_title}{ext}")

        except Exception as e:
            self.clean_temp(folder, temp_filename); return 2 if "Stopped" in str(e) else 1

        if self.stop_event.is_set(): self.clean_temp(folder, temp_filename); return 2

        if use_hb:
            try:
                if "Auto" in hb_preset:
                    is_4k = video_width > 2600 or video_height >= 2160
                    preset = "Fast 2160p60 4K HEVC" if is_4k else "Fast 1080p30" if video_height >= 1080 else "Fast 720p30"
                else:
                    if "Fast 2160p" in hb_preset: preset = "Fast 2160p60 4K HEVC"
                    elif "HQ 2160p" in hb_preset: preset = "HQ 2160p60 4K HEVC Surround"
                    else: preset = hb_preset

                self.status_var.set(f"Processing ({preset})...")
                self.progress_bar.configure(mode="indeterminate"); self.progress_bar.start()

                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

                self.current_process = subprocess.Popen([
                    self.handbrake_path, "-i", temp_fullpath, "-o", final_output, "-Z", preset, "-e", "x264", "--all-audio"
                ], startupinfo=startupinfo, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                self.current_process.wait()
                
                if self.stop_event.is_set() or self.current_process.returncode != 0:
                    self.clean_temp(folder, temp_filename)
                    if os.path.exists(final_output): os.remove(final_output)
                    return 2
                
                if os.path.exists(temp_fullpath): os.remove(temp_fullpath)
                self.after(0, self.finish_success); return 0

            except Exception as e:
                self.clean_temp(folder, temp_filename)
                self.after(0, lambda: self.finish_fail(f"Processing Error: {str(e)[:30]}")); return 2
        else:
            try:
                if os.path.exists(final_output): os.remove(final_output)
                os.rename(temp_fullpath, final_output)
                self.after(0, self.finish_success); return 0
            except: return 2

    def clean_temp(self, folder, filename):
        for f in glob.glob(os.path.join(folder, f"{filename}.*")): os.remove(f)

    def finish_success(self):
        self.progress_bar.stop(); self.progress_bar.configure(mode="determinate"); self.progress_bar.set(1.0)
        self.status_var.set("Process Complete"); self.status_label.configure(text_color=C_SUCCESS)
        self.reset_common(); self.after(7000, self.clear_status_completely)

    def finish_fail(self, message):
        self.progress_bar.stop(); self.progress_bar.configure(mode="determinate")
        self.status_var.set(message); self.status_label.configure(text_color=C_ERROR)
        self.reset_common()

    def reset_common(self):
        self.downloading = False; self.current_process = None
        self.download_btn.configure(text="START DOWNLOAD", fg_color=self.current_accent, hover_color=self.current_accent_hover, command=self.initiate_download)
        self.format_switch.configure(state="normal"); self.res_menu.configure(state="normal")
        self.hb_checkbox.configure(state="normal"); self.toggle_hb_menu()
        self.audio_fmt_menu.configure(state="normal"); self.update_options_visibility(self.format_var.get())

if __name__ == "__main__":
    ff, hb = check_tool_dependencies()
    hide_console()
    app = ModernDownloaderApp(ff, hb)
    app.mainloop()