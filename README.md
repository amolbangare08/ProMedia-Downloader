# ProMedia Downloader 🎬  
High-Fidelity **YouTube Video Downloader for Premiere Pro, DaVinci Resolve, and After Effects** (VFR to CFR Fix)

**ProMedia Downloader** is a Windows tool that lets video editors download YouTube videos in the highest quality and automatically convert **VFR (Variable Frame Rate)** to **CFR (Constant Frame Rate)** using HandBrake, so clips play smoothly in professional NLEs like Adobe Premiere Pro, DaVinci Resolve, and After Effects.

![App Screenshot](screenshot.png)

---

## What Is ProMedia Downloader?

ProMedia Downloader is a **YouTube downloader for video editors** that solves audio desync and timeline glitches caused by variable frame rate footage. 
Instead of juggling multiple tools (yt-dlp + HandBrake + manual settings), it provides a **one-click workflow**: paste URL → get an edit-ready CFR MP4.

**Core keywords this project targets:**

- YouTube downloader for Premiere Pro  
- Fix variable frame rate (VFR) for editing  
- Convert VFR to CFR with HandBrake  
- YouTube to MP4 (H.264, CFR) for NLEs  
- Video downloader for DaVinci Resolve / After Effects

---

## 🛑 The Problem: YouTube + VFR in NLEs

Most online videos (especially YouTube) use **Variable Frame Rate (VFR)** encoding.
This is great for streaming efficiency, but terrible for professional editing.

Typical problems editors face:

- Video plays smoothly in VLC, but **lags, stutters, or feels choppy** on the timeline  
- **Audio and video drift out of sync** in long clips  
- Premiere Pro and other NLEs show **“Variable frame rate detected”** warnings or behave unpredictably with the footage. 
- The manual workaround is to open each clip in **HandBrake**, configure CFR settings, then re‑encode before importing.

If you download a lot of YouTube clips for tutorials, breakdowns, reactions, or reference, this adds friction to every project.

---

## ✅ The Solution: One-Click VFR → CFR YouTube Downloader

**ProMedia Downloader** automates that workflow end-to-end:

1. Downloads the **highest-quality YouTube video + audio stream** available.  
2. Sends the file through a **HandBrake-based CFR conversion pipeline** in the background.
3. Outputs an **MP4 (H.264, Constant Frame Rate)** file that drops cleanly into:
   - Adobe Premiere Pro  
   - DaVinci Resolve  
   - After Effects  
   - Other NLEs that prefer CFR media

You paste a YouTube link and receive an **edit-ready master file** designed specifically for professional timelines.

---

## ✨ Key Features

- **YouTube Downloader for Editors**  
  Purpose-built for video editors who need robust, edit-safe files, not just “watchable” downloads.

- **Automatic VFR to CFR Conversion (HandBrake)**  
  Automatically converts **Variable Frame Rate to Constant Frame Rate** using HandBrake under the hood, removing the need to open HandBrake manually for every clip.

- **High-Quality 4K & 8K Support**  
  Downloads the best available YouTube quality (up to **4K, 8K, and high-FPS** streams when present), ideal for breakdowns, zoom-ins, and reframing.

- **Smart Proxy / Anti-Block System**  
  Uses a rotating proxy list to help bypass common **bot checks, sign‑in prompts, and basic region restrictions** that sometimes block high-quality downloads.

- **Flexible Output Formats**  
  Choose what you need for your project:
  - **Video + Audio**: Full edit-ready master file (MP4, H.264, CFR)  
  - **Video Only**: For relinking or separate audio workflows  
  - **Audio Only (MP3/WAV)**: For music, sound design, or dialogue reference

- **Editor-Friendly UI (Dark / Light)**  
  Clean, minimal desktop UI with **Dark and Light themes** that follow your Windows accent color; fits naturally into a pro-editing environment.

- **No Python Required for Binary Build**  
  The packaged `.exe` is a **standalone Windows app**—no Python runtime, no CLI, no complex setup required.

---

## 🚀 Installation & Setup

### Option 1: Download the Windows EXE (Recommended)

This is the easiest way for most editors.

1. Open the **[Releases page](https://github.com/amolbangare08/ProMedia-Downloader/releases)**.  
2. Download the latest `ProMedia.Downloader.exe`.  
3. Run the app:
   - No installer  
   - No Python  
   - No command line required

> Tip: Place the `.exe` in a fixed folder (e.g., `C:\Tools\ProMedia\`) and create a desktop or Start Menu shortcut for quick access.

---

### Option 2: Run From Source (Developers)

If you want to modify or extend the app:

1. Clone the repository:
git clone https://github.com/amolbangare08/ProMedia-Downloader.git
cd ProMedia-Downloader