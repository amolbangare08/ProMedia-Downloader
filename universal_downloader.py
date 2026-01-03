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
from yt_dlp.utils import download_range_func

from core import *

# --- MAIN UI ---
from ui import UIMixin
from downloaders import DownloaderMixin

class ModernDownloaderApp(UIMixin, DownloaderMixin):
    pass

if __name__ == "__main__":
    ff, hb = check_tool_dependencies()
    hide_console()
    app = ModernDownloaderApp(ff, hb)
    app.mainloop()