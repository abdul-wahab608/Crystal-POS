const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const { findAvailablePort } = require('./port-utils.cjs');
const SimplifiedSetup = require('./simplified-setup.cjs');

let mainWindow;
let djangoProcess = null;
const isDev = process.env.NODE_ENV === 'development';

// User data directory for storing database and config
const userDataPath = app.getPath('userData');
const configPath = path.join(userDataPath, 'config.json');
const dbPath = path.join(userDataPath, 'db.sqlite3');

// Setup manager
let setupManager = null;

// Initialize setup manager
function initSetup() {
  if (!setupManager) {
    setupManager = new SimplifiedSetup(app, userDataPath);
  }
  return setupManager;
}

// Check if first run
function isFirstRun() {
  const setup = initSetup();
  return !setup.isSetupComplete();
}

// Mark setup as complete
function markSetupComplete() {
  // Setup completion is now tracked by SimplifiedSetup
  // This function kept for compatibility
  console.log('Setup marked complete');
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
    // Production mode - load built files from app resources
    const indexPath = path.join(__dirname, '../dist/index.html');
    console.log('Loading production build from:', indexPath);
    mainWindow.loadFile(indexPath);
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Start Django backend
async function startBackend() {
  return new Promise((resolve, reject) => {
    const config = loadConfig();
    
    let backendCmd, backendArgs, backendCwd;
    
    if (isDev) {
      // Development mode - use system Python
      backendCwd = path.join(__dirname, '../../backend');
      backendCmd = 'python';
      backendArgs = ['manage.py', 'runserver', `127.0.0.1:${config.backendPort}`, '--noreload'];
    } else {
      // Production mode - use bundled Python
      const pythonPath = path.join(userDataPath, 'python', 'python.exe');
      backendCwd = path.join(process.resourcesPath, 'backend');
      backendCmd = pythonPath;
      backendArgs = ['manage.py', 'runserver', `127.0.0.1:${config.backendPort}`, '--noreload'];
      
      console.log('Using bundled Python:', pythonPath);
    }

    // Set environment variables
    const env = {
      ...process.env,
      DJANGO_DB_PATH: config.dbPath,
      DJANGO_SECRET_KEY: 'desktop-app-secret-key-' + Date.now(),
      DJANGO_PORT: config.backendPort.toString(),
      PYTHONPATH: backendCwd
    };

    console.log('Starting Django backend...');
    console.log('Backend command:', backendCmd);
    console.log('Backend args:', backendArgs);
    console.log('Backend path:', backendCwd);
    console.log('Database path:', config.dbPath);

    djangoProcess = spawn(backendCmd, backendArgs, {
      cwd: backendCwd,
      env: env,
      shell: true,
      windowsHide: false  // Show window for debugging
    });

    let startupTimeout;

    djangoProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log(`Django: ${output}`);
      
      // Check if server started successfully
      if (output.includes('Starting development server') || output.includes('Quit the server')) {
        if (startupTimeout) clearTimeout(startupTimeout);
        setTimeout(() => resolve(), 2000);
      }
    });

    djangoProcess.stderr.on('data', (data) => {
      console.error(`Django Error: ${data}`);
    });

    djangoProcess.on('error', (error) => {
      console.error('Failed to start Django:', error);
      if (startupTimeout) clearTimeout(startupTimeout);
      // Don't reject - just log and continue
      resolve();
    });

    djangoProcess.on('close', (code) => {
      console.log(`Django process exited with code ${code}`);
      if (code !== 0 && code !== null) {
        console.error('Django exited with error code:', code);
      }
      djangoProcess = null;
    });

    // Timeout fallback - resolve after 8 seconds even if we don't see the message
    startupTimeout = setTimeout(() => {
      console.log('Backend startup timeout reached, proceeding...');
      resolve();
    }, 8000);
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
  
  const setup = initSetup();
  
  // Run setup with progress logging
  const result = await setup.runSetup((status, progress, message) => {
    console.log(`Setup: ${status} ${progress}% - ${message}`);
  });
  
  if (!result.success) {
    console.error('Setup failed:', result.error);
    throw new Error(result.error);
  }
  
  console.log('First-time setup completed successfully');
  return result;
}

// IPC Handlers
ipcMain.handle('get-config', () => {
  const config = loadConfig();
  console.log('Sending config to renderer:', config);
  return config;
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

// Simplified setup handler
ipcMain.handle('run-setup', async () => {
  try {
    const setup = initSetup();
    const result = await setup.runSetup((status, progress, message) => {
      console.log(`Setup: ${status} ${progress}% - ${message}`);
    });
    return result;
  } catch (error) {
    console.error('Setup error:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-sync-queue', () => {
  // This would integrate with the frontend's offline manager
  // For now, return a placeholder
  return { total: 0, items: [] };
});

ipcMain.handle('clear-sync-queue', () => {
  // Clear sync queue - handled by frontend for now
  return { success: true };
});

// App lifecycle
app.whenReady().then(async () => {
  try {
    // Check if first run
    if (isFirstRun()) {
      await runFirstTimeSetup();
    }

    // Find available port for backend
    const config = loadConfig();
    const availablePort = await findAvailablePort(config.backendPort);
    
    if (availablePort !== config.backendPort) {
      console.log(`Port ${config.backendPort} is in use, using port ${availablePort}`);
      config.backendPort = availablePort;
      saveConfig(config);
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
