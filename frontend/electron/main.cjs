const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const { findAvailablePort } = require('./port-utils.cjs');
const SetupStateManager = require('./setup-state.cjs');
const PythonInstaller = require('./scripts/python-installer.cjs');
const DependencyInstaller = require('./scripts/dependency-installer.cjs');
const DatabaseSetup = require('./scripts/database-setup.cjs');

let mainWindow;
let djangoProcess = null;
const isDev = process.env.NODE_ENV === 'development';
let pythonExecutablePath = null; // Store Python path for reuse

// User data directory for storing database and config
const userDataPath = app.getPath('userData');
const configPath = path.join(userDataPath, 'config.json');
const dbPath = path.join(userDataPath, 'db.sqlite3');

// Setup state manager
let setupState = null;

// Initialize setup state manager
function initSetupState() {
  if (!setupState) {
    setupState = new SetupStateManager(userDataPath);
  }
  return setupState;
}

// Check if first run
function isFirstRun() {
  const state = initSetupState();
  return state.isFirstRun();
}

// Mark setup as complete
function markSetupComplete() {
  const state = initSetupState();
  state.markComplete(app.getVersion());
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
    console.log('Backend args:', backendArgs);
    console.log('Backend path:', backendCwd);
    console.log('Database path:', config.dbPath);

    // Test: Try running Python first to see if it's accessible
    try {
      const testPython = spawn('python', ['--version'], { shell: true });
      testPython.stdout.on('data', (data) => console.log(`Python test: ${data}`));
      testPython.stderr.on('data', (data) => console.log(`Python test: ${data}`));
    } catch (err) {
      console.error('Python test failed:', err);
    }

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
  console.log('Running first-time setup wizard...');
  
  // Show setup wizard window
  const setupWindow = new BrowserWindow({
    width: 700,
    height: 650,
    resizable: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false
    },
    frame: true,
    title: 'Crystal POS - First Time Setup'
  });

  setupWindow.loadFile(path.join(__dirname, 'setup-wizard.html'));

  // Wait for setup to complete
  return new Promise((resolve) => {
    ipcMain.once('setup-complete', () => {
      console.log('Setup wizard completed successfully');
      markSetupComplete();
      setupWindow.close();
      resolve();
    });
    
    // Handle window close without completing setup
    setupWindow.on('closed', () => {
      console.log('Setup window closed');
      // Mark as complete anyway to prevent infinite loop
      markSetupComplete();
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

ipcMain.handle('get-setup-state', () => {
  const state = initSetupState();
  return state.getState();
});

ipcMain.handle('reset-setup', () => {
  const state = initSetupState();
  state.reset();
  return { success: true, message: 'Setup state reset successfully' };
});

ipcMain.handle('check-setup-status', async (event, step) => {
  console.log(`Checking setup status for: ${step}`);
  
  const state = initSetupState();
  
  try {
    // Update step to 'working'
    state.updateStep(step, 'working');
    
    // Execute step-specific logic
    switch (step) {
      case 'python':
        await setupPython(state);
        break;
      
      case 'dependencies':
        await setupDependencies(state);
        break;
      
      case 'database':
        await setupDatabase(state);
        break;
      
      case 'admin':
        await setupAdmin(state);
        break;
      
      default:
        throw new Error(`Unknown setup step: ${step}`);
    }
    
    // Mark step as complete
    state.updateStep(step, 'complete');
    
    return { 
      success: true, 
      step,
      progress: state.getProgress()
    };
  } catch (error) {
    console.error(`Setup error for ${step}:`, error);
    state.updateStep(step, 'error', error.message);
    
    return { 
      success: false, 
      step,
      error: error.message
    };
  }
});

/**
 * Setup Python - Phase 2
 */
async function setupPython(state) {
  console.log('Starting Python setup...');
  
  const pythonInstaller = new PythonInstaller(userDataPath, console);
  
  // Check if Python exists
  const check = await pythonInstaller.isPythonInstalled();
  
  if (check.installed) {
    console.log(`Python already installed: ${check.path} (${check.type})`);
    
    // Verify version
    try {
      const version = await pythonInstaller.getPythonVersion(check.path);
      console.log(`Python version: ${version}`);
    } catch (err) {
      console.warn('Could not get Python version:', err);
    }
    
    // Store Python path for later use
    pythonExecutablePath = check.path;
    
    return { success: true, path: check.path };
  }
  
  // Python not found - install it
  console.log('Python not found, installing...');
  
  const result = await pythonInstaller.install((status, progress) => {
    console.log(`Python installation: ${status} ${progress}%`);
  });
  
  if (!result.success) {
    throw new Error('Failed to install Python');
  }
  
  // Store Python path
  pythonExecutablePath = result.path;
  
  console.log('Python setup complete:', result.path);
  return result;
}

/**
 * Setup Dependencies - Phase 3
 */
async function setupDependencies(state) {
  console.log('Starting dependencies setup...');
  
  // Ensure we have Python path
  if (!pythonExecutablePath) {
    throw new Error('Python path not available. Run Python setup first.');
  }

  // Get backend path
  const backendPath = isDev 
    ? path.join(__dirname, '../../backend')
    : path.join(process.resourcesPath, 'backend');

  console.log('Backend path:', backendPath);
  console.log('Python path:', pythonExecutablePath);

  const depInstaller = new DependencyInstaller(pythonExecutablePath, backendPath, console);

  // Check if requirements.txt exists
  if (!depInstaller.requirementsExists()) {
    throw new Error('requirements.txt not found in backend folder');
  }

  // Check if already installed
  const alreadyInstalled = await depInstaller.areDependenciesInstalled();
  
  if (alreadyInstalled) {
    console.log('Dependencies already installed');
    return { success: true, message: 'Dependencies already installed' };
  }

  // Upgrade pip first
  console.log('Upgrading pip...');
  await depInstaller.upgradePip();

  // Install dependencies
  console.log('Installing dependencies from requirements.txt...');
  const result = await depInstaller.install((status, progress, message) => {
    console.log(`Dependencies: ${status} ${progress}% - ${message}`);
  });

  console.log(`Dependencies setup complete: ${result.packagesInstalled} packages installed`);
  return result;
}

/**
 * Setup Database - Phase 4 (Part 1: Migrations)
 */
async function setupDatabase(state) {
  console.log('Starting database setup...');
  
  // Ensure we have Python path
  if (!pythonExecutablePath) {
    throw new Error('Python path not available. Run Python setup first.');
  }

  // Get backend path
  const backendPath = isDev 
    ? path.join(__dirname, '../../backend')
    : path.join(process.resourcesPath, 'backend');

  console.log('Backend path:', backendPath);
  console.log('Python path:', pythonExecutablePath);
  console.log('Database path:', dbPath);

  const dbSetup = new DatabaseSetup(pythonExecutablePath, backendPath, dbPath, console);

  // Check if manage.py exists
  if (!dbSetup.managePyExists()) {
    throw new Error('manage.py not found in backend folder');
  }

  // Run migrations
  console.log('Running database migrations...');
  const result = await dbSetup.migrate((status, progress) => {
    console.log(`Database migrations: ${status} ${progress}%`);
  });

  if (!result.success) {
    throw new Error('Failed to run migrations');
  }

  console.log('Database setup complete');
  return result;
}

/**
 * Setup Admin - Phase 4 (Part 2: Create Admin User)
 */
async function setupAdmin(state) {
  console.log('Starting admin user creation...');
  
  // Ensure we have Python path
  if (!pythonExecutablePath) {
    throw new Error('Python path not available. Run Python setup first.');
  }

  // Get backend path
  const backendPath = isDev 
    ? path.join(__dirname, '../../backend')
    : path.join(process.resourcesPath, 'backend');

  const dbSetup = new DatabaseSetup(pythonExecutablePath, backendPath, dbPath, console);

  // Create admin user
  console.log('Creating admin user (admin/admin123)...');
  const result = await dbSetup.createAdmin('admin', 'admin123', 'admin@crystal.com');

  if (!result.success) {
    throw new Error('Failed to create admin user');
  }

  if (result.created) {
    console.log(`Admin user created: ${result.username} / ${result.password}`);
  } else {
    console.log('Admin user already exists');
  }

  return result;
}

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
        console.log('Creating new database with migrations...');
        const { spawn } = require('child_process');
        const pythonCmd = 'python';
        const migrateProcess = spawn(pythonCmd, ['manage.py', 'migrate', '--noinput'], {
          cwd: backendPath,
          env: {
            ...process.env,
            DJANGO_DB_PATH: config.dbPath,
            DJANGO_SECRET_KEY: 'desktop-app-secret-key-' + Date.now()
          },
          shell: true
        });
        
        migrateProcess.stdout.on('data', (data) => {
          console.log(`Migration: ${data}`);
        });
        
        migrateProcess.stderr.on('data', (data) => {
          console.error(`Migration error: ${data}`);
        });
        
        await new Promise((resolve, reject) => {
          migrateProcess.on('close', (code) => {
            if (code === 0) {
              console.log('Migrations completed successfully');
              resolve();
            } else {
              console.error(`Migrations failed with code ${code}`);
              reject(new Error(`Migration failed with code ${code}`));
            }
          });
          
          migrateProcess.on('error', (err) => {
            console.error('Migration process error:', err);
            reject(err);
          });
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
