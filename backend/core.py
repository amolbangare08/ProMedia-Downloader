import os
import sys
import ctypes
import winreg
import socket
import random
import glob
import shutil
import zipfile
import tkinter as tk
import requests

# --- 3. SYSTEM ACCENT COLOR ---
def get_windows_accent():
    try:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\DWM")
        value, type = winreg.QueryValueEx(key, "ColorizationColor")
        return f"#{hex(value)[4:]}"
    except:
        return "#6366f1"

# --- 4. FONT LOADER ---
def load_custom_fonts():
    font_files = ["Poppins-Regular.ttf", "Poppins-Bold.ttf"]
    fonts_loaded = False
    
    base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
    
    for font_file in font_files:
        font_path = os.path.join(base_path, font_file)
        if os.path.exists(font_path):
            try:
                res = ctypes.windll.gdi32.AddFontResourceExW(font_path, 0x10, 0)
                if res > 0:
                    fonts_loaded = True
            except: pass
    
    return "Poppins" if fonts_loaded else "Segoe UI"

# --- 5. ADAPTIVE COLOR PALETTE ---
C_BG           = ("#ffffff", "#09090b") 
C_CARD         = ("#f4f4f5", "#18181b") 
C_CARD_BORDER  = ("#e4e4e7", "#27272a") 

C_TEXT_MAIN    = ("#18181b", "#fafafa") 
C_TEXT_SUB     = ("#71717a", "#a1a1aa") 

C_INPUT_BG     = ("#ffffff", "#09090b")
C_INPUT_BORDER = ("#d4d4d8", "#3f3f46") 

C_SEGMENT_UNSELECTED = ("#a1a1aa", "#27272a") 
C_SEGMENT_TEXT       = "#ffffff"

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

def parse_time_to_seconds(time_str):
    """Converts various time formats to integer seconds"""
    if not time_str: return 0
    try:
        # If user types raw seconds (e.g. "90")
        if time_str.isdigit():
            return int(time_str)
            
        parts = list(map(int, time_str.strip().split(':')))
        if len(parts) == 3: return parts[0]*3600 + parts[1]*60 + parts[2] # HH:MM:SS
        if len(parts) == 2: return parts[0]*60 + parts[1] # MM:SS
        return parts[0] # SS
    except: return 0

def format_seconds_to_str(seconds):
    """Converts integer seconds back to MM:SS or HH:MM:SS"""
    if seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m:02d}:{s:02d}"
    else:
        h, remainder = divmod(seconds, 3600)
        m, s = divmod(remainder, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

def check_tool_dependencies():
    cwd = os.getcwd()
    ffmpeg_path = os.path.join(cwd, "ffmpeg.exe")
    handbrake_path = os.path.join(cwd, "HandBrakeCLI.exe")

    if not os.path.exists(ffmpeg_path):
        if shutil.which("ffmpeg"): ffmpeg_path = shutil.which("ffmpeg")
        else:
            try:
                r = requests.get(FFMPEG_URL, stream=True)
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
            r = requests.get(HANDBRAKE_URL, headers=h, stream=True)
            if r.status_code == 200:
                with open("handbrake.zip", 'wb') as f: shutil.copyfileobj(r.raw, f)
                with zipfile.ZipFile("handbrake.zip", 'r') as z:
                    for i in z.infolist():
                        if i.filename.endswith("HandBrakeCLI.exe"):
                            i.filename = "HandBrakeCLI.exe"; z.extract(i, cwd); break
                os.remove("handbrake.zip")
        except: pass

    return ffmpeg_path, handbrake_path

APP_FONT = load_custom_fonts()

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
                          relief="flat", borderwidth=0, font=(APP_FONT, 9), padx=8, pady=6)
        label.pack()

    def hide_tip(self, event=None):
        if self.tipwindow: self.tipwindow.destroy(); self.tipwindow = None