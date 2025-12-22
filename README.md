# ProMedia Downloader 🎬

**The High-Fidelity YouTube Downloader & VFR Converter for Video Editors.**

![App Screenshot](screenshot.png)

> **Fix YouTube glitches in Premiere Pro & DaVinci Resolve automatically.**
> *Keywords: YouTube to MP4 4K, Fix VFR Audio Sync, HandBrake Automation, Variable Frame Rate Fix, Premiere Pro Glitch Fix.*

## 🛑 The Problem: "Why does my footage glitch?"
As a video editor, you know the pain:
1. You download a clip from YouTube using a random website.
2. It plays fine in VLC, but **glitches, lags, or de-syncs** when imported into **Adobe Premiere Pro** or **DaVinci Resolve**.
3. **The Cause:** YouTube videos use **VFR (Variable Frame Rate)** to save data. Professional NLEs require **CFR (Constant Frame Rate)** to edit smoothly.
4. **The Old Fix:** You had to manually waste time converting every clip through HandBrake before editing.

## ✅ The Solution: "One Click, Edit Ready"
**ProMedia Downloader** automates the entire workflow. It downloads the highest bitrate stream and **automatically passes it through the HandBrake engine** in the background.

**The Result:** You get a buttery smooth, edit-ready **MP4 (H.264, CFR)** file that works perfectly in Premiere Pro, DaVinci Resolve, After Effects, and Sony Vegas. No manual transcoding required.

## ✨ Key Features
- **Auto-HandBrake Integration:** Instantly converts VFR to CFR (Constant Frame Rate).
- **4K & 8K Resolution:** Downloads the highest quality video streams available (2160p/4320p).
- **Lossless Audio Extraction:** Extract audio tracks as high-quality MP3, WAV, or M4A.
- **Smart Proxy System:** Bypasses "Sign-in required" or "Bot detected" errors using rotating proxies.
- **Cross-Platform:** Native Windows App (.exe) or run via Python on Linux/macOS.
- **Modern UI:** Professional Dark/Light themes that sync with your system accent color.

---

## 🚀 How to Install

### 🔹 Option 1: The Easy Way (Windows Only)
*Best for editors who just want it to work.*
1. Go to the [**Releases Page**](https://github.com/amolbangare08/ProMedia-Downloader/releases).
2. Download the latest `ProMedia.Downloader.exe`.
3. Run the app. (FFmpeg and HandBrake engines will be downloaded automatically on the first run).

### 🔹 Option 2: Run from Source (Windows, Linux, macOS)
*Best for developers or Linux users.*

**Prerequisites:** Ensure you have [Python 3.10+](https://www.python.org/downloads/) installed.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/amolbangare08/ProMedia-Downloader.git](https://github.com/amolbangare08/ProMedia-Downloader.git)
   cd ProMedia-Downloader

```

2. **Install dependencies:**
```bash
pip install -r requirements.txt

```


3. **Run the script:**
* **Windows:** `python youtube_downloader.py`
* **Linux/Mac:** `python3 youtube_downloader.py`



*(Note for Linux Users: You may need to install ffmpeg and HandBrakeCLI via your package manager, e.g., `sudo apt install ffmpeg handbrake-cli`)*

---

## 🛡️ Advanced: How to Use Proxies

If you are downloading many videos and YouTube temporarily blocks your IP (errors like "HTTP 429" or "Sign in to confirm you're not a bot"), you can use proxies.

1. Create a new text file named **`proxies.txt`** in the same folder as the app.
2. Add your proxy URLs, one per line. Supported formats:
```text
[http://user:pass@123.45.67.89:8080](http://user:pass@123.45.67.89:8080)
socks5://123.45.67.89:1080
[http://123.45.67.89:3128](http://123.45.67.89:3128)

```


3. **Restart the app.**
4. If a download fails due to network blocking, the app will automatically switch to "Secure Proxy Mode" and rotate through your list until it finds a working connection.

---

## 🤝 Contributing

Found a bug? Want to add a feature?

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.


*Built by Editors, for Editors.*

