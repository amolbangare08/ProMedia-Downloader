const { ipcRenderer } = require('electron');

// --- ELEMENTS ---
const el = (id) => document.getElementById(id);

// 1. Inputs (Values)
const urlInput = el('url');
const qualitySelect = el('quality');      // The dropdown
const audioFmtSelect = el('audio-fmt');   // The dropdown
const hbPresetSelect = el('hb-preset');   // <--- FIXED: Added this definition

// 2. Toggles & Buttons
const trimCheck = el('chk-trim');
const hbCheck = el('chk-hb');
const btnDownload = el('btn-download');

// 3. Cards/Containers (For showing/hiding)
const qualityCard = el('quality-card');
const audioFmtCard = el('audio-fmt-card');
const hbCard = el('hb-card');
const hbPresetCard = el('hb-preset-card');
const trimInputsCard = el('trim-inputs-card');

// 4. Status Elements
const statusText = el('status');
const progressFill = el('progress-fill');
const progressContainer = el('progress-container');

// --- STATE ---
let currentMode = 'video_audio';
let isDownloading = false;

// --- 1. MODE SWITCHING ---
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
        // Audio Mode
        if(qualityCard) qualityCard.style.display = 'none';
        if(audioFmtCard) audioFmtCard.style.display = 'flex'; 
        if(hbCard) hbCard.style.display = 'none';
        if(hbPresetCard) hbPresetCard.style.display = 'none';
    } else {
        // Video Modes
        if(qualityCard) qualityCard.style.display = 'flex';
        if(audioFmtCard) audioFmtCard.style.display = 'none';
        if(hbCard) hbCard.style.display = 'flex';
        
        // Only show preset if Handbrake is CHECKED
        if(hbPresetCard) {
            hbPresetCard.style.display = hbCheck.checked ? 'flex' : 'none';
        }
    }
}

// --- 2. OPTION TOGGLES ---
if (trimCheck) {
    trimCheck.addEventListener('change', () => {
        if(trimInputsCard) trimInputsCard.style.display = trimCheck.checked ? 'block' : 'none';
    });
}

if (hbCheck) {
    hbCheck.addEventListener('change', () => {
        if(hbPresetCard) hbPresetCard.style.display = hbCheck.checked ? 'flex' : 'none';
    });
}

// --- 3. TIME AUTO-FORMATTER ---
function formatTime(input) {
    const val = input.value.trim();
    if (!val) return;

    let seconds = 0;
    if (/^\d+$/.test(val)) {
        seconds = parseInt(val);
    } else if (val.includes(':')) {
        const parts = val.split(':').map(Number);
        if (parts.length === 2) seconds = parts[0] * 60 + parts[1];
        if (parts.length === 3) seconds = parts[0] * 3600 + parts[1] * 60 + parts[2];
    } else {
        return;
    }

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

// --- 5. START DOWNLOAD ---
btnDownload.addEventListener('click', () => {
    // STOP LOGIC
    if (isDownloading) {
        ipcRenderer.send('stop-download');
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
    statusText.innerText = "Select folder...";
    statusText.style.color = "var(--text-sub)";

    // Prepare Data Packet
    // Map internal mode names to what Python expects
    let pythonMode = "Video + Audio";
    if (currentMode === 'video_only') pythonMode = "Video Only";
    if (currentMode === 'audio_only') pythonMode = "Audio Only";

    const args = {
        url: url,
        mode: pythonMode,
        res: qualitySelect.value,
        audio_fmt: audioFmtSelect.value,
        use_hb: hbCheck.checked,
        hb_preset: hbPresetSelect.value, // <--- FIXED: Now uses the defined variable
        trim_on: trimCheck.checked,
        t_start: el('t-start').value,
        t_end: el('t-end').value
    };

    console.log("Sending to main:", args);
    ipcRenderer.send('start-download', args);
});

// --- 6. LISTENERS ---
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

ipcRenderer.on('download-canceled', () => {
    statusText.innerText = "Download canceled";
    resetUI();
});

ipcRenderer.on('download-stopped', () => {
    statusText.innerText = "Download Stopped";
    statusText.style.color = "var(--text-sub)";
    resetUI();
});

function resetUI() {
    isDownloading = false;
    btnDownload.innerText = "START DOWNLOAD";
    btnDownload.classList.remove('stop');
}

// Initial Run
updateVisibility();