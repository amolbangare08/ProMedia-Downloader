const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 1200,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
    icon: path.join(__dirname, 'app.ico'), // Set the app icon
  });

  win.loadFile('frontend/index.html');

  // Maintain square aspect ratio on resize
  win.on('resize', () => {
    const [width, height] = win.getSize();
    const size = Math.max(width, height);
    win.setSize(size, size);
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});