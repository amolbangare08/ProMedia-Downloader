import os
import re
import tkinter as tk
import customtkinter as ctk
import threading
from tkinter import filedialog
from core import *

class UIMixin(ctk.CTk):
    def __init__(self, ffmpeg_path, handbrake_path):
        super().__init__()
        self.ffmpeg_path = ffmpeg_path
        self.handbrake_path = handbrake_path
        self.stop_event = threading.Event()
        self.current_process = None
        self.downloading = False
        
        icon_path = resource_path("app.ico")
        if os.path.exists(icon_path): self.iconbitmap(icon_path)
        self.title("Universal Downloader")
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

        # Top bar
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 0))
        
        self.theme_menu = ctk.CTkOptionMenu(
            self.top_bar, values=["Light", "Dark", "System"], command=self.change_theme,
            width=90, height=28, font=(APP_FONT, 11), fg_color=C_CARD_BORDER,
            text_color=C_TEXT_MAIN, button_color=C_INPUT_BORDER, button_hover_color=C_TEXT_SUB
        )
        self.theme_menu.pack(side="right")
        ctk.CTkLabel(self.top_bar, text="Theme:", font=(APP_FONT, 11), text_color=C_TEXT_SUB).pack(side="right", padx=5)

        self.accent_menu = ctk.CTkOptionMenu(
            self.top_bar, values=["Indigo", "Windows System", "Emerald", "Blue"], command=self.change_accent,
            width=130, height=28, font=(APP_FONT, 11), fg_color=C_CARD_BORDER,
            text_color=C_TEXT_MAIN, button_color=C_INPUT_BORDER, button_hover_color=C_TEXT_SUB
        )
        self.accent_menu.pack(side="right", padx=(0, 20))
        ctk.CTkLabel(self.top_bar, text="Accent:", font=(APP_FONT, 11), text_color=C_TEXT_SUB).pack(side="right", padx=5)

        # Main content
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self.card = ctk.CTkFrame(self.main_container, corner_radius=24, fg_color=C_CARD, border_width=1, border_color=C_CARD_BORDER)
        self.card.grid(row=0, column=0, sticky="ew")

        # Header
        self.title_label = ctk.CTkLabel(self.card, text="Universal Downloader", font=(APP_FONT, 30, "bold"), text_color=C_TEXT_MAIN)
        self.title_label.pack(pady=(40, 5))
        self.subtitle_label = ctk.CTkLabel(self.card, text="Universal Media Extractor", font=(APP_FONT, 12), text_color=C_TEXT_SUB)
        self.subtitle_label.pack(pady=(0, 30))

        # Input
        self.input_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=50)
        
        self.url_entry = ctk.CTkEntry(
            self.input_frame, textvariable=self.url_var, placeholder_text="Paste YouTube link here...", height=50,
            font=(APP_FONT, 13), border_width=1, border_color=C_INPUT_BORDER, fg_color=C_INPUT_BG, text_color=C_TEXT_MAIN, corner_radius=12
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.url_entry.bind("<KeyRelease>", self.clear_status)

        self.paste_btn = ctk.CTkButton(
            self.input_frame, text="PASTE", width=100, height=50, font=(APP_FONT, 12, "bold"),
            fg_color=self.current_accent, hover_color=self.current_accent_hover, text_color="#ffffff", corner_radius=12,
            command=self.paste_clipboard
        )
        self.paste_btn.pack(side="right")

        # Controls
        self.controls_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.controls_frame.pack(pady=25, padx=50, fill="x")

        self.format_var = ctk.StringVar(value="Video + Audio")
        self.format_switch = ctk.CTkSegmentedButton(
            self.controls_frame, values=["Video + Audio", "Video Only", "Audio Only"], variable=self.format_var,
            font=(APP_FONT, 12, "bold"), height=40, corner_radius=10,
            selected_color=self.current_accent, selected_hover_color=self.current_accent_hover,
            unselected_color=C_SEGMENT_UNSELECTED, unselected_hover_color=C_INPUT_BORDER, 
            text_color=C_SEGMENT_TEXT, 
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
            text_color=C_TEXT_MAIN, font=(APP_FONT, 12), dropdown_fg_color=C_CARD, dropdown_text_color=C_TEXT_MAIN
        )

        self.trim_var = ctk.BooleanVar(value=False)
        self.trim_checkbox = ctk.CTkCheckBox(
            self.options_container, text="Cut/Trim", variable=self.trim_var,
            font=(APP_FONT, 12), text_color=C_TEXT_MAIN, border_color=C_TEXT_SUB,
            hover_color=self.current_accent, fg_color=self.current_accent, checkmark_color="white",
            command=self.toggle_trim_inputs
        )
        

        self.trim_frame = ctk.CTkFrame(self.options_container, fg_color="transparent")
        
        self.start_time_entry = ctk.CTkEntry(
            self.trim_frame, placeholder_text="00:00", width=60, height=35,
            font=(APP_FONT, 12), border_width=1, border_color=C_INPUT_BORDER, fg_color=C_INPUT_BG, text_color=C_TEXT_MAIN
        )
        self.trim_sep = ctk.CTkLabel(self.trim_frame, text="-", text_color=C_TEXT_MAIN)
        self.end_time_entry = ctk.CTkEntry(
            self.trim_frame, placeholder_text="00:15", width=60, height=35,
            font=(APP_FONT, 12), border_width=1, border_color=C_INPUT_BORDER, fg_color=C_INPUT_BG, text_color=C_TEXT_MAIN
        )
        self.start_time_entry.pack(side="left"); self.trim_sep.pack(side="left", padx=5); self.end_time_entry.pack(side="left")

        # --- BINDING FOR AUTO-FORMATTING ---
        # When user clicks away (FocusOut) or hits Enter (Return), formatting runs
        self.start_time_entry.bind("<FocusOut>", lambda e: self.auto_format_time_field(self.start_time_entry))
        self.start_time_entry.bind("<Return>", lambda e: self.auto_format_time_field(self.start_time_entry))
        
        self.end_time_entry.bind("<FocusOut>", lambda e: self.auto_format_time_field(self.end_time_entry))
        self.end_time_entry.bind("<Return>", lambda e: self.auto_format_time_field(self.end_time_entry))
        # -----------------------------------

        self.use_hb_var = ctk.BooleanVar(value=False)
        self.hb_checkbox = ctk.CTkCheckBox(
            self.options_container, text="Optimize (HandBrake)", variable=self.use_hb_var,
            font=(APP_FONT, 12), text_color=C_TEXT_MAIN, border_color=C_TEXT_SUB,
            hover_color=self.current_accent, fg_color=self.current_accent, checkmark_color="white",
            command=self.toggle_hb_menu
        )
        ToolTip(self.hb_checkbox, "Fixes VFR glitches & audio sync. Essential for Premiere Pro & DaVinci Resolve.")

        self.hb_preset_var = ctk.StringVar(value="Auto (Smart Match)")
        self.hb_menu = ctk.CTkOptionMenu(
            self.options_container,
            values=["Auto (Smart Match)", "Fast 1080p30", "HQ 1080p30 Surround", "Fast 2160p60 4K", "HQ 2160p60 4K", "Fast 720p30", "Production Standard"],
            variable=self.hb_preset_var, width=180, height=35, fg_color=C_INPUT_BG, button_color=C_INPUT_BORDER,
            button_hover_color=C_CARD_BORDER, text_color=C_TEXT_MAIN, font=(APP_FONT, 12), dropdown_fg_color=C_CARD
        )

        self.audio_fmt_var = ctk.StringVar(value="mp3")
        self.audio_fmt_menu = ctk.CTkOptionMenu(
            self.options_container, values=["mp3", "m4a", "wav", "flac"], variable=self.audio_fmt_var,
            width=100, height=35, fg_color=C_INPUT_BG, button_color=C_INPUT_BORDER, text_color=C_TEXT_MAIN, font=(APP_FONT, 12),
            dropdown_fg_color=C_CARD, dropdown_text_color=C_TEXT_MAIN
        )
        self.update_options_visibility("Video + Audio")

        # Action Area
        self.action_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.action_frame.pack(pady=(10, 30), padx=50, fill="x", side="bottom")

        self.status_label = ctk.CTkLabel(self.action_frame, textvariable=self.status_var, text_color=C_TEXT_SUB, font=(APP_FONT, 11))
        self.status_label.pack(side="bottom", pady=(5, 0))

        self.progress_bar = ctk.CTkProgressBar(self.action_frame, height=6, corner_radius=3, progress_color=self.current_accent, fg_color=C_INPUT_BORDER)
        self.progress_bar.set(0)

        self.download_btn = ctk.CTkButton(
            self.action_frame, text="START DOWNLOAD", font=(APP_FONT, 13, "bold"), height=55, corner_radius=12,
            fg_color=self.current_accent, hover_color=self.current_accent_hover, text_color="#ffffff",
            command=self.initiate_download
        )
        self.download_btn.pack(fill="x", pady=(0, 15))

    # --- NEW: AUTO FORMATTER LOGIC ---
    def auto_format_time_field(self, entry_widget):
        raw_text = entry_widget.get().strip()
        if not raw_text: return
        
        # If user typed digits only (e.g. "90"), we treat it as seconds
        # If user typed "1:30", parse_time handles that too
        seconds = parse_time_to_seconds(raw_text)
        formatted = format_seconds_to_str(seconds)
        
        # Update UI with clean format
        entry_widget.delete(0, "end")
        entry_widget.insert(0, formatted)
        
        # Move focus back to main window if Enter was pressed
        self.focus_set()

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
        self.trim_checkbox.configure(hover_color=self.current_accent, fg_color=self.current_accent)
        self.progress_bar.configure(progress_color=self.current_accent)

    # --- UI LOGIC ---
    def toggle_hb_menu(self):
        state = "normal" if self.use_hb_var.get() else "disabled"
        self.hb_menu.configure(state=state)

    def toggle_trim_inputs(self):
        self.update_options_visibility(self.format_var.get())

    def update_options_visibility(self, choice):
        for w in self.options_container.winfo_children(): w.pack_forget()
        
        if choice == "Audio Only": 
            self.audio_fmt_menu.pack(side="left")
            self.trim_checkbox.pack(side="left", padx=(15, 10))
            if self.trim_var.get(): self.trim_frame.pack(side="left", padx=(0, 15))
        else: 
            self.res_menu.pack(side="left", padx=(0, 15))
            self.trim_checkbox.pack(side="left", padx=(0, 10))
            if self.trim_var.get(): self.trim_frame.pack(side="left", padx=(0, 15))
            
            self.hb_checkbox.pack(side="left", padx=(0, 10))
            self.hb_menu.pack(side="left")

    def clear_status(self, event=None):
        if not self.downloading: self.status_var.set(""); self.status_label.configure(text_color=C_TEXT_SUB)

    def clear_status_completely(self):
        if not self.downloading: self.status_var.set(""); self.progress_bar.pack_forget()

    def paste_clipboard(self):
        try: self.url_var.set(self.clipboard_get()); self.clear_status() 
        except: pass

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

        trim_on = self.trim_var.get()
        t_start = self.start_time_entry.get() if trim_on else None
        t_end = self.end_time_entry.get() if trim_on else None

        self.downloading = True
        self.download_btn.configure(text="STOP DOWNLOAD", fg_color=C_STOP, hover_color=C_STOP_HOVER, command=self.stop_process)
        self.progress_bar.pack(fill="x", pady=(0, 10), before=self.status_label)
        self.progress_bar.set(0)
        
        self.format_switch.configure(state="disabled"); self.res_menu.configure(state="disabled"); 
        self.hb_checkbox.configure(state="disabled"); self.hb_menu.configure(state="disabled"); 
        self.audio_fmt_menu.configure(state="disabled"); self.trim_checkbox.configure(state="disabled")
        
        threading.Thread(target=self.run_download_manager, 
                          args=(url, folder, self.format_var.get(), self.res_var.get(), 
                                self.audio_fmt_var.get(), self.use_hb_var.get(), 
                                self.hb_preset_var.get(), trim_on, t_start, t_end), 
                          daemon=True).start()