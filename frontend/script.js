const { ipcRenderer } = require('electron');

// --- ELEMENTS ---
const el = (id) => document.getElementById(id);
const urlInput = el('url');
const qualityCard = el('quality-card');
const audioFmtCard = el('audio-fmt-card');
const trimCheck = el('chk-trim');
const trimInputsCard = el('trim-inputs-card');
const hbCheck = el('chk-hb');
const hbCard = el('hb-card');
const hbPresetCard = el('hb-preset-card');
const btnDownload = el('btn-download');
const statusText = el('status');
const progressFill = el('progress-fill');
const progressContainer = el('progress-container');

// --- STATE ---
let currentMode = 'video_audio';
let isDownloading = false;

// --- 1. MODE SWITCHING (The Segmented Control) ---
document.querySelectorAll('.segment-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Visual Update
        document.querySelectorAll('.segment-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Logic Update
        currentMode = btn.dataset.mode;
        updateVisibility();
    });
});

function updateVisibility() {
    if (currentMode === 'audio_only') {
        qualityCard.style.display = 'none';
        audioFmtCard.style.display = 'flex'; // Use flex for cards
        hbCard.style.display = 'none';
        hbPresetCard.style.display = 'none';
    } else {
        qualityCard.style.display = 'flex';
        audioFmtCard.style.display = 'none';
        hbCard.style.display = 'flex';

        // Check checkbox state for preset
        hbPresetCard.style.display = hbCheck.checked ? 'flex' : 'none';
    }
}

// --- 2. OPTION TOGGLES ---
trimCheck.addEventListener('change', () => {
    trimInputsCard.style.display = trimCheck.checked ? 'block' : 'none';
});

hbCheck.addEventListener('change', () => {
    hbPresetCard.style.display = hbCheck.checked ? 'flex' : 'none';
});

// --- 3. TIME AUTO-FORMATTER (The "Smart" Feature) ---
// Matches python's format_seconds_to_str logic
function formatTime(input) {
    const val = input.value.trim();
    if (!val) return;

    let seconds = 0;
    if (/^\d+$/.test(val)) {
        seconds = parseInt(val); // User typed "90" -> 90s
    } else if (val.includes(':')) {
        const parts = val.split(':').map(Number);
        if (parts.length === 2) seconds = parts[0] * 60 + parts[1];
        if (parts.length === 3) seconds = parts[0] * 3600 + parts[1] * 60 + parts[2];
    } else {
        return;
    }

    // Convert back to MM:SS or HH:MM:SS
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;

    if (h > 0) {
        input.value = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    } else {
        input.value = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }
}

el('t-start').addEventListener('blur', (e) => formatTime(e.target));
el('t-end').addEventListener('blur', (e) => formatTime(e.target));
el('t-start').addEventListener('keydown', (e) => { if(e.key === 'Enter') formatTime(e.target) });
el('t-end').addEventListener('keydown', (e) => { if(e.key === 'Enter') formatTime(e.target) });

// --- 4. PASTE BUTTON ---
el('btn-paste').addEventListener('click', async () => {
    const text = await navigator.clipboard.readText();
    urlInput.value = text;
});

// --- 5. START DOWNLOAD (Sending data to Main) ---
btnDownload.addEventListener('click', () => {
    if (isDownloading) {
        // Handle STOP logic here later
        return;
    }

    const url = urlInput.value.trim();
    if (!url) {
        statusText.innerText = "Please enter a valid URL";
        statusText.style.color = "var(--danger)";
        return;
    }

    // Lock UI
    isDownloading = true;
    btnDownload.innerText = "STOP DOWNLOAD";
    btnDownload.classList.add('stop');
    progressContainer.style.display = 'block';
    progressFill.style.width = '0%';
    statusText.innerText = "Initializing...";
    statusText.style.color = "var(--text-sub)";

    // Prepare Data Packet
    const args = {
        url: url,
        mode: currentMode === 'video_audio' ? 'Video + Audio' : (currentMode === 'video_only' ? 'Video Only' : 'Audio Only'),
        folder: "", // Logic for folder dialog will be added
        res: qualitySelect.value,
        audio_fmt: audioFmtSelect.value,
        use_hb: hbCheck.checked,
        hb_preset: hbPreset.value,
        trim_on: trimCheck.checked,
        t_start: el('t-start').value,
        t_end: el('t-end').value
    };

    // Send to main process
    ipcRenderer.send('start-download', args);
});

// --- 6. RECEIVE UPDATES ---
ipcRenderer.on('python-output', (event, msg) => {
    if (msg.type === 'progress') {
        const percent = msg.data * 100;
        progressFill.style.width = percent + '%';
        statusText.innerText = msg.text || `Downloading... ${Math.round(percent)}%`;
    } 
    else if (msg.type === 'success') {
        statusText.innerText = "Download Complete!";
        statusText.style.color = "var(--success)";
        resetUI();
    }
    else if (msg.type === 'error') {
        statusText.innerText = "Error: " + msg.data;
        statusText.style.color = "var(--danger)";
        resetUI();
    }
});

function resetUI() {
    isDownloading = false;
    btnDownload.innerText = "START DOWNLOAD";
    btnDownload.classList.remove('stop');
    // progressContainer.style.display = 'none'; // Optional: keep it shown on success
}

// Initial Run
updateVisibility();