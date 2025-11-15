const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const { findAvailablePort } = require('./port-utils.cjs');

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
    
    let backendCmd, backendArgs, backendCwd;
    
    if (isDev) {
      // Development mode - use Python directly
      backendCwd = path.join(__dirname, '../../backend');
      backendCmd = 'python';
      backendArgs = ['manage.py', 'runserver', `127.0.0.1:${config.backendPort}`, '--noreload'];
    } else {
      // Production mode - use bundled executable
      const exePath = path.join(process.resourcesPath, 'backend', 'crystal-backend.exe');
      
      // Fallback to Python if executable doesn't exist
      if (fs.existsSync(exePath)) {
        backendCmd = exePath;
        backendArgs = [];
        backendCwd = path.join(process.resourcesPath, 'backend');
      } else {
        // Fallback: try Python in production
        backendCwd = path.join(process.resourcesPath, 'backend');
        backendCmd = 'python';
        backendArgs = ['manage.py', 'runserver', `127.0.0.1:${config.backendPort}`, '--noreload'];
      }
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
    console.log('Backend path:', backendCwd);
    console.log('Database path:', config.dbPath);

    djangoProcess = spawn(backendCmd, backendArgs, {
      cwd: backendCwd,
      env: env,
      shell: true
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
      reject(error);
    });

    djangoProcess.on('close', (code) => {
      console.log(`Django process exited with code ${code}`);
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

ipcMain.handle('get-sync-queue', () => {
  // This would integrate with the frontend's offline manager
  // For now, return a placeholder
  return { total: 0, items: [] };
});

ipcMain.handle('clear-sync-queue', () => {
  // Clear sync queue - handled by frontend for now
  return { success: true };
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
        console.log('Database copied to:', config.dbPath);
      } else {
        // Run migrations to create fresh database
        console.log('Creating new database...');
        const { spawn } = require('child_process');
        const pythonCmd = 'python';
        const migrateProcess = spawn(pythonCmd, ['manage.py', 'migrate'], {
          cwd: backendPath,
          env: {
            ...process.env,
            DJANGO_DB_PATH: config.dbPath
          },
          shell: true
        });
        
        await new Promise((resolve) => {
          migrateProcess.on('close', () => resolve());
        });
      }
    }
    
    // Ensure user data directory exists
    if (!fs.existsSync(userDataPath)) {
      fs.mkdirSync(userDataPath, { recursive: true });
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
