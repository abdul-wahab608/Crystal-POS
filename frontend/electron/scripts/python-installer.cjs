const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const https = require('https');
const { pipeline } = require('stream');
const { promisify } = require('util');

const streamPipeline = promisify(pipeline);

/**
 * Python Installer Module
 * Detects Python installation and installs if missing
 */

class PythonInstaller {
  constructor(userDataPath, logger = console) {
    this.userDataPath = userDataPath;
    this.logger = logger;
    this.pythonDir = path.join(userDataPath, 'python');
    this.pythonExe = null;
    
    // Python embeddable package URL (Windows x64)
    // Using Python 3.11.9 (stable version compatible with Django 5.x)
    this.pythonVersion = '3.11.9';
    this.pythonDownloadUrl = `https://www.python.org/ftp/python/${this.pythonVersion}/python-${this.pythonVersion}-embed-amd64.zip`;
    this.pythonZipPath = path.join(userDataPath, 'python-embed.zip');
  }

  /**
   * Check if Python is installed (system or bundled)
   */
  async isPythonInstalled() {
    this.logger.log('Checking for Python installation...');
    
    // First check bundled Python
    const bundledPython = path.join(this.pythonDir, 'python.exe');
    if (fs.existsSync(bundledPython)) {
      this.pythonExe = bundledPython;
      this.logger.log('Found bundled Python:', bundledPython);
      return { installed: true, path: bundledPython, type: 'bundled' };
    }

    // Check system Python
    const systemPython = await this.checkSystemPython();
    if (systemPython) {
      this.pythonExe = systemPython;
      this.logger.log('Found system Python:', systemPython);
      return { installed: true, path: systemPython, type: 'system' };
    }

    this.logger.log('Python not found');
    return { installed: false, path: null, type: null };
  }

  /**
   * Check if system Python is available
   */
  async checkSystemPython() {
    return new Promise((resolve) => {
      const pythonCommands = ['python', 'python3', 'py'];
      
      const tryCommand = (index) => {
        if (index >= pythonCommands.length) {
          resolve(null);
          return;
        }

        const cmd = pythonCommands[index];
        const process = spawn(cmd, ['--version'], { shell: true });
        
        let output = '';
        process.stdout.on('data', (data) => { output += data.toString(); });
        process.stderr.on('data', (data) => { output += data.toString(); });
        
        process.on('close', (code) => {
          if (code === 0 && output.includes('Python')) {
            this.logger.log(`Found Python via '${cmd}':`, output.trim());
            resolve(cmd);
          } else {
            tryCommand(index + 1);
          }
        });

        process.on('error', () => {
          tryCommand(index + 1);
        });
      };

      tryCommand(0);
    });
  }

  /**
   * Get Python version
   */
  async getPythonVersion(pythonCmd = null) {
    const cmd = pythonCmd || this.pythonExe || 'python';
    
    return new Promise((resolve, reject) => {
      const process = spawn(cmd, ['--version'], { shell: true });
      
      let output = '';
      process.stdout.on('data', (data) => { output += data.toString(); });
      process.stderr.on('data', (data) => { output += data.toString(); });
      
      process.on('close', (code) => {
        if (code === 0) {
          const match = output.match(/Python (\d+\.\d+\.\d+)/);
          resolve(match ? match[1] : 'unknown');
        } else {
          reject(new Error('Failed to get Python version'));
        }
      });

      process.on('error', reject);
    });
  }

  /**
   * Download Python embeddable package
   */
  async downloadPython(onProgress = null) {
    this.logger.log('Downloading Python embeddable package...');
    this.logger.log('URL:', this.pythonDownloadUrl);

    // Ensure directory exists
    if (!fs.existsSync(this.userDataPath)) {
      fs.mkdirSync(this.userDataPath, { recursive: true });
    }

    return new Promise((resolve, reject) => {
      const file = fs.createWriteStream(this.pythonZipPath);
      
      https.get(this.pythonDownloadUrl, (response) => {
        if (response.statusCode !== 200) {
          reject(new Error(`Download failed: HTTP ${response.statusCode}`));
          return;
        }

        const totalSize = parseInt(response.headers['content-length'], 10);
        let downloadedSize = 0;

        response.on('data', (chunk) => {
          downloadedSize += chunk.length;
          if (onProgress) {
            const percent = Math.round((downloadedSize / totalSize) * 100);
            onProgress(percent, downloadedSize, totalSize);
          }
        });

        response.pipe(file);

        file.on('finish', () => {
          file.close();
          this.logger.log('Python download complete');
          resolve(this.pythonZipPath);
        });

      }).on('error', (err) => {
        fs.unlink(this.pythonZipPath, () => {});
        reject(err);
      });
    });
  }

  /**
   * Extract Python package
   */
  async extractPython() {
    this.logger.log('Extracting Python...');

    // Use Node.js built-in extract-zip or fallback to PowerShell
    try {
      // Create python directory
      if (!fs.existsSync(this.pythonDir)) {
        fs.mkdirSync(this.pythonDir, { recursive: true });
      }

      // Use PowerShell to extract (built-in on Windows)
      await this.extractWithPowerShell(this.pythonZipPath, this.pythonDir);
      
      this.logger.log('Python extracted successfully to:', this.pythonDir);
      
      // Set pythonExe path
      this.pythonExe = path.join(this.pythonDir, 'python.exe');
      
      // Clean up zip file
      fs.unlinkSync(this.pythonZipPath);
      
      return this.pythonExe;

    } catch (error) {
      this.logger.error('Failed to extract Python:', error);
      throw error;
    }
  }

  /**
   * Extract zip using PowerShell
   */
  async extractWithPowerShell(zipPath, destPath) {
    return new Promise((resolve, reject) => {
      const psCommand = `Expand-Archive -Path "${zipPath}" -DestinationPath "${destPath}" -Force`;
      
      const process = spawn('powershell', ['-Command', psCommand], { shell: true });
      
      process.on('close', (code) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`PowerShell extraction failed with code ${code}`));
        }
      });

      process.on('error', reject);
    });
  }

  /**
   * Setup pip for embedded Python
   */
  async setupPip() {
    this.logger.log('Setting up pip for embedded Python...');

    try {
      // Download get-pip.py
      const getPipUrl = 'https://bootstrap.pypa.io/get-pip.py';
      const getPipPath = path.join(this.pythonDir, 'get-pip.py');

      await this.downloadFile(getPipUrl, getPipPath);

      // Run get-pip.py
      await this.runPythonCommand([getPipPath]);

      this.logger.log('Pip installed successfully');

    } catch (error) {
      this.logger.error('Failed to setup pip:', error);
      throw error;
    }
  }

  /**
   * Download a file
   */
  async downloadFile(url, destPath) {
    return new Promise((resolve, reject) => {
      const file = fs.createWriteStream(destPath);
      
      https.get(url, (response) => {
        if (response.statusCode !== 200) {
          reject(new Error(`Download failed: HTTP ${response.statusCode}`));
          return;
        }

        response.pipe(file);

        file.on('finish', () => {
          file.close();
          resolve(destPath);
        });

      }).on('error', (err) => {
        fs.unlink(destPath, () => {});
        reject(err);
      });
    });
  }

  /**
   * Run Python command
   */
  async runPythonCommand(args, options = {}) {
    const pythonCmd = this.pythonExe || 'python';
    
    return new Promise((resolve, reject) => {
      this.logger.log('Running Python command:', pythonCmd, args.join(' '));
      
      const process = spawn(pythonCmd, args, {
        ...options,
        shell: true
      });

      let stdout = '';
      let stderr = '';

      process.stdout.on('data', (data) => {
        stdout += data.toString();
        this.logger.log(data.toString());
      });

      process.stderr.on('data', (data) => {
        stderr += data.toString();
        this.logger.log(data.toString());
      });

      process.on('close', (code) => {
        if (code === 0) {
          resolve({ stdout, stderr, code });
        } else {
          reject(new Error(`Python command failed with code ${code}\n${stderr}`));
        }
      });

      process.on('error', reject);
    });
  }

  /**
   * Install Python (full process)
   */
  async install(onProgress = null) {
    this.logger.log('Starting Python installation process...');

    try {
      // Check if already installed
      const check = await this.isPythonInstalled();
      if (check.installed) {
        this.logger.log('Python already installed:', check.path);
        return { success: true, path: check.path, message: 'Python already installed' };
      }

      // Download Python
      if (onProgress) onProgress('downloading', 0);
      await this.downloadPython((percent) => {
        if (onProgress) onProgress('downloading', percent);
      });

      // Extract Python
      if (onProgress) onProgress('extracting', 100);
      await this.extractPython();

      // Setup pip
      if (onProgress) onProgress('configuring', 100);
      await this.setupPip();

      this.logger.log('Python installation complete!');
      
      return { 
        success: true, 
        path: this.pythonExe, 
        message: 'Python installed successfully' 
      };

    } catch (error) {
      this.logger.error('Python installation failed:', error);
      throw error;
    }
  }

  /**
   * Get Python executable path
   */
  getPythonPath() {
    return this.pythonExe;
  }
}

module.exports = PythonInstaller;
