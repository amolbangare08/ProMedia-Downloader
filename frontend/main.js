const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let childProcess = null; // Global variable to store the running Python process

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 850,
    height: 850,
    title: "Universal Downloader",
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  mainWindow.loadFile('index.html');
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// --- START DOWNLOAD ---
ipcMain.on('start-download', async (event, args) => {
  const { url, mode, res, audio_fmt, use_hb, hb_preset, trim_on, t_start, t_end } = args;

  const scriptPath = path.join(__dirname, '..', 'backend', 'cli.py');

  // 1. Select Folder
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory'],
    title: 'Select Download Folder'
  });

  if (result.canceled) {
    mainWindow.webContents.send('download-canceled');
    return;
  }

  const folder = result.filePaths[0];

  // 2. Prepare Arguments
  const cliArgs = [
    scriptPath,
    url,
    '--folder', folder,
    '--mode', mode,
    '--res', res,
    '--audio_fmt', audio_fmt,
    '--hb_preset', hb_preset
  ];

  if (use_hb) cliArgs.push('--use_hb');
  if (trim_on) {
    cliArgs.push('--trim_on');
    cliArgs.push('--trim_start', t_start);
    cliArgs.push('--trim_end', t_end);
  }

  // 3. Spawn Python (Assign to global variable)
  // Ensure we kill any existing process first
  if (childProcess) {
    try { childProcess.kill(); } catch(e){}
  }

  childProcess = spawn('python', cliArgs);

  // 4. Listen for Output (FIXED: Uses 'childProcess' instead of 'child')
  childProcess.stdout.on('data', (data) => {
    const lines = data.toString().split('\n');
    lines.forEach(line => {
      if (!line.trim()) return;
      try {
        const json = JSON.parse(line);
        mainWindow.webContents.send('python-output', json);
      } catch (e) {
        // Ignore non-JSON output
      }
    });
  });

  childProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`);
  });

  childProcess.on('close', (code) => {
      childProcess = null;
  });
});

// --- STOP DOWNLOAD ---
ipcMain.on('stop-download', () => {
    if (childProcess) {
        childProcess.kill();
        childProcess = null;
    }
    mainWindow.webContents.send('download-stopped');
});