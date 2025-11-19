/**
 * Crystal POS - Simplified Setup Module
 * PRODUCTION APPROACH: Extract bundled Python, run migrations, done!
 * No downloads, no network dependency, 100% reliable
 */

const { ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

class SimplifiedSetup {
  constructor(app, userDataPath) {
    this.app = app;
    this.userDataPath = userDataPath;
    this.dbPath = path.join(userDataPath, 'db.sqlite3');
    this.stateFile = path.join(userDataPath, '.setup_complete');
    
    // Python will be extracted from bundled resources
    this.pythonPath = null;
  }

  /**
   * Check if setup is complete
   */
  isSetupComplete() {
    return fs.existsSync(this.stateFile);
  }

  /**
   * Mark setup as complete
   */
  markComplete() {
    fs.writeFileSync(this.stateFile, JSON.stringify({
      completed: true,
      timestamp: new Date().toISOString(),
      version: this.app.getVersion()
    }));
  }

  /**
   * Extract bundled Python to user data directory
   */
  async extractPython(onProgress) {
    const resourcesPath = process.resourcesPath || path.join(__dirname, '../../');
    const bundledPython = path.join(resourcesPath, 'python-runtime', 'python');
    const extractedPython = path.join(this.userDataPath, 'python');

    if (fs.existsSync(extractedPython)) {
      console.log('Python already extracted');
      this.pythonPath = path.join(extractedPython, 'python.exe');
      return { success: true, path: this.pythonPath };
    }

    console.log('Extracting bundled Python...');
    onProgress && onProgress('Extracting Python runtime...', 20);

    try {
      // Copy entire Python directory
      await this.copyDirectory(bundledPython, extractedPython);
      
      this.pythonPath = path.join(extractedPython, 'python.exe');
      
      console.log('Python extracted to:', this.pythonPath);
      onProgress && onProgress('Python ready', 40);
      
      return { success: true, path: this.pythonPath };
    } catch (error) {
      console.error('Failed to extract Python:', error);
      throw new Error(`Python extraction failed: ${error.message}`);
    }
  }

  /**
   * Copy directory recursively
   */
  async copyDirectory(src, dest) {
    await fs.promises.mkdir(dest, { recursive: true });
    
    const entries = await fs.promises.readdir(src, { withFileTypes: true });
    
    for (const entry of entries) {
      const srcPath = path.join(src, entry.name);
      const destPath = path.join(dest, entry.name);
      
      if (entry.isDirectory()) {
        await this.copyDirectory(srcPath, destPath);
      } else {
        await fs.promises.copyFile(srcPath, destPath);
      }
    }
  }

  /**
   * Run Django migrations
   */
  async runMigrations(onProgress) {
    console.log('Running database migrations...');
    onProgress && onProgress('Setting up database...', 60);

    const backendPath = process.resourcesPath 
      ? path.join(process.resourcesPath, 'backend')
      : path.join(__dirname, '../../../backend');

    return new Promise((resolve, reject) => {
      const proc = spawn(this.pythonPath, [
        path.join(backendPath, 'manage.py'),
        'migrate',
        '--noinput'
      ], {
        env: {
          ...process.env,
          DJANGO_DB_PATH: this.dbPath,
          DJANGO_SECRET_KEY: 'production-key-' + Date.now(),
          PYTHONIOENCODING: 'utf-8'
        },
        cwd: backendPath
      });

      let output = '';

      proc.stdout.on('data', (data) => {
        output += data.toString();
        console.log(data.toString());
      });

      proc.stderr.on('data', (data) => {
        output += data.toString();
        console.log(data.toString());
      });

      proc.on('close', (code) => {
        if (code === 0) {
          console.log('Migrations completed');
          onProgress && onProgress('Database ready', 80);
          resolve({ success: true });
        } else {
          reject(new Error(`Migrations failed with code ${code}`));
        }
      });

      proc.on('error', reject);
    });
  }

  /**
   * Create admin user
   */
  async createAdminUser(onProgress) {
    console.log('Creating admin user...');
    onProgress && onProgress('Creating admin account...', 90);

    const backendPath = process.resourcesPath 
      ? path.join(process.resourcesPath, 'backend')
      : path.join(__dirname, '../../../backend');

    const command = `
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@crystal.com', 'admin123');
    print('Admin user created');
else:
    print('Admin user already exists');
`;

    return new Promise((resolve, reject) => {
      const proc = spawn(this.pythonPath, [
        path.join(backendPath, 'manage.py'),
        'shell',
        '-c',
        command
      ], {
        env: {
          ...process.env,
          DJANGO_DB_PATH: this.dbPath,
          DJANGO_SECRET_KEY: 'production-key-' + Date.now(),
          PYTHONIOENCODING: 'utf-8'
        },
        cwd: backendPath
      });

      let output = '';

      proc.stdout.on('data', (data) => {
        output += data.toString();
        console.log(data.toString());
      });

      proc.stderr.on('data', (data) => {
        console.log(data.toString());
      });

      proc.on('close', (code) => {
        if (code === 0) {
          console.log('Admin user ready');
          onProgress && onProgress('Setup complete!', 100);
          resolve({ success: true, username: 'admin', password: 'admin123' });
        } else {
          reject(new Error(`Admin creation failed with code ${code}`));
        }
      });

      proc.on('error', reject);
    });
  }

  /**
   * Run complete setup
   */
  async runSetup(onProgress) {
    try {
      onProgress && onProgress('Starting setup...', 0);

      // Step 1: Extract Python
      await this.extractPython(onProgress);

      // Step 2: Run migrations
      await this.runMigrations(onProgress);

      // Step 3: Create admin user
      await this.createAdminUser(onProgress);

      // Mark complete
      this.markComplete();

      return { success: true };
    } catch (error) {
      console.error('Setup failed:', error);
      throw error;
    }
  }
}

module.exports = SimplifiedSetup;
