const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

let mainWindow;
let djangoProcess = null;
const isDev = process.env.NODE_ENV === 'development';

// User data directory for storing database and config
const userDataPath = app.getPath('userData');
const configPath = path.join(userDataPath, 'config.json');
const dbPath = path.join(userDataPath, 'db.sqlite3');
const setupCompletePath = path.join(userDataPath, '.setup_complete');

// Check if first run
function isFirstRun() {
  return !fs.existsSync(setupCompletePath);
}

// Mark setup as complete
function markSetupComplete() {
  fs.writeFileSync(setupCompletePath, JSON.stringify({
    completedAt: new Date().toISOString(),
    version: app.getVersion()
  }));
}

// Load or create config
function loadConfig() {
  if (fs.existsSync(configPath)) {
    return JSON.parse(fs.readFileSync(configPath, 'utf8'));
  }
  
  const defaultConfig = {
    backendPort: 8000,
    firstRun: true,
    dbPath: dbPath
  };
  
  fs.writeFileSync(configPath, JSON.stringify(defaultConfig, null, 2));
  return defaultConfig;
}

// Save config
function saveConfig(config) {
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
}

// Create main window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 768,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false
    },
    icon: path.join(__dirname, '../public/favicon.ico'),
    show: false // Don't show until ready
  });

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  if (isDev) {
    // Development mode - load Vite dev server
    const vitePort = process.env.VITE_PORT || 5173;
    mainWindow.loadURL(`http://localhost:${vitePort}`);
    mainWindow.webContents.openDevTools();
  } else {
    // Production mode - load built files
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Start Django backend
async function startBackend() {
  return new Promise((resolve, reject) => {
    const config = loadConfig();
    const backendPath = isDev 
      ? path.join(__dirname, '../../backend')
      : path.join(process.resourcesPath, 'backend');
    
    const pythonCmd = isDev ? 'python' : path.join(backendPath, 'python', 'python.exe');
    const managePath = path.join(backendPath, 'manage.py');

    // Set environment variable for database path
    const env = {
      ...process.env,
      DJANGO_DB_PATH: config.dbPath,
      DJANGO_SECRET_KEY: 'desktop-app-secret-key-' + Date.now(),
      PYTHONPATH: backendPath
    };

    console.log('Starting Django backend...');
    console.log('Backend path:', backendPath);
    console.log('Database path:', config.dbPath);

    djangoProcess = spawn(pythonCmd, [managePath, 'runserver', `127.0.0.1:${config.backendPort}`, '--noreload'], {
      cwd: backendPath,
      env: env,
      shell: true
    });

    djangoProcess.stdout.on('data', (data) => {
      console.log(`Django: ${data}`);
      if (data.toString().includes('Starting development server')) {
        setTimeout(() => resolve(), 2000); // Wait 2s for server to fully start
      }
    });

    djangoProcess.stderr.on('data', (data) => {
      console.error(`Django Error: ${data}`);
    });

    djangoProcess.on('error', (error) => {
      console.error('Failed to start Django:', error);
      reject(error);
    });

    djangoProcess.on('close', (code) => {
      console.log(`Django process exited with code ${code}`);
      djangoProcess = null;
    });

    // Timeout fallback
    setTimeout(() => resolve(), 5000);
  });
}

// Stop Django backend
function stopBackend() {
  if (djangoProcess) {
    console.log('Stopping Django backend...');
    djangoProcess.kill();
    djangoProcess = null;
  }
}

// Setup process - only runs on first launch
async function runFirstTimeSetup() {
  console.log('Running first-time setup...');
  
  // Show setup window
  const setupWindow = new BrowserWindow({
    width: 600,
    height: 400,
    resizable: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true
    }
  });

  setupWindow.loadFile(path.join(__dirname, 'setup.html'));

  // Wait for setup to complete (simulated here)
  return new Promise((resolve) => {
    ipcMain.once('setup-complete', () => {
      markSetupComplete();
      setupWindow.close();
      resolve();
    });
  });
}

// IPC Handlers
ipcMain.handle('get-config', () => {
  return loadConfig();
});

ipcMain.handle('save-config', (event, config) => {
  saveConfig(config);
  return { success: true };
});

ipcMain.handle('get-user-data-path', () => {
  return userDataPath;
});

ipcMain.handle('is-first-run', () => {
  return isFirstRun();
});

ipcMain.handle('start-setup', async () => {
  try {
    const config = loadConfig();
    const backendPath = path.join(__dirname, '../../backend');
    
    // Copy database if it doesn't exist
    if (!fs.existsSync(config.dbPath)) {
      const sourceDb = path.join(backendPath, 'db.sqlite3');
      if (fs.existsSync(sourceDb)) {
        fs.copyFileSync(sourceDb, config.dbPath);
      }
    }
    
    markSetupComplete();
    return { success: true };
  } catch (error) {
    console.error('Setup error:', error);
    return { success: false, error: error.message };
  }
});

// App lifecycle
app.whenReady().then(async () => {
  try {
    // Check if first run
    if (isFirstRun()) {
      await runFirstTimeSetup();
    }

    // Start Django backend
    await startBackend();

    // Create main window
    createWindow();
  } catch (error) {
    console.error('Failed to start application:', error);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

app.on('before-quit', () => {
  stopBackend();
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
});
