const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * Dependency Installer Module
 * Installs Python packages from requirements.txt
 */

class DependencyInstaller {
  constructor(pythonPath, backendPath, logger = console) {
    this.pythonPath = pythonPath;
    this.backendPath = backendPath;
    this.logger = logger;
    this.requirementsPath = path.join(backendPath, 'requirements.txt');
  }

  /**
   * Check if requirements.txt exists
   */
  requirementsExists() {
    return fs.existsSync(this.requirementsPath);
  }

  /**
   * Read requirements.txt
   */
  readRequirements() {
    if (!this.requirementsExists()) {
      throw new Error('requirements.txt not found at: ' + this.requirementsPath);
    }

    const content = fs.readFileSync(this.requirementsPath, 'utf8');
    return content
      .split('\n')
      .map(line => line.trim())
      .filter(line => line && !line.startsWith('#'))
      .map(line => {
        // Parse package name and version
        const match = line.match(/^([a-zA-Z0-9\-_]+)(.*)/);
        return match ? { raw: line, name: match[1], version: match[2] } : null;
      })
      .filter(pkg => pkg !== null);
  }

  /**
   * Check if a package is installed
   */
  async isPackageInstalled(packageName) {
    return new Promise((resolve) => {
      const process = spawn(this.pythonPath, ['-m', 'pip', 'show', packageName], {
        shell: true,
        windowsHide: true
      });

      process.on('close', (code) => {
        resolve(code === 0);
      });

      process.on('error', () => {
        resolve(false);
      });
    });
  }

  /**
   * Check if all dependencies are installed
   */
  async areDependenciesInstalled() {
    this.logger.log('Checking installed dependencies...');

    if (!this.requirementsExists()) {
      this.logger.warn('requirements.txt not found');
      return false;
    }

    try {
      const packages = this.readRequirements();
      this.logger.log(`Found ${packages.length} packages in requirements.txt`);

      // Check key packages (Django is critical)
      const keyPackages = ['django', 'djangorestframework', 'django-cors-headers'];
      
      for (const pkg of keyPackages) {
        const installed = await this.isPackageInstalled(pkg);
        if (!installed) {
          this.logger.log(`Key package not installed: ${pkg}`);
          return false;
        }
      }

      this.logger.log('All key dependencies appear to be installed');
      return true;

    } catch (error) {
      this.logger.error('Error checking dependencies:', error);
      return false;
    }
  }

  /**
   * Install dependencies from requirements.txt
   */
  async install(onProgress = null) {
    this.logger.log('Starting dependency installation...');

    if (!this.requirementsExists()) {
      throw new Error('requirements.txt not found');
    }

    return new Promise((resolve, reject) => {
      // Use pip install with requirements.txt
      // Removed --upgrade to avoid conflicts, added --no-cache-dir for embedded Python
      const args = [
        '-m', 'pip', 'install',
        '-r', this.requirementsPath,
        '--no-cache-dir',
        '--no-warn-script-location',
        '--disable-pip-version-check'
      ];

      this.logger.log('Running pip install:', this.pythonPath, args.join(' '));

      const process = spawn(this.pythonPath, args, {
        shell: true,
        cwd: this.backendPath,
        windowsHide: false,
        env: {
          ...process.env,
          PYTHONIOENCODING: 'utf-8',
          PYTHONUNBUFFERED: '1'
        }
      });

      let stdout = '';
      let stderr = '';
      let packageCount = 0;
      const packages = this.readRequirements();
      const totalPackages = packages.length;

      process.stdout.on('data', (data) => {
        const output = data.toString();
        stdout += output;
        
        // Log output
        this.logger.log(output.trim());

        // Track progress
        if (output.includes('Collecting') || output.includes('Downloading')) {
          packageCount++;
          const progress = Math.round((packageCount / totalPackages) * 100);
          if (onProgress) {
            onProgress('installing', progress, output.trim());
          }
        }
      });

      process.stderr.on('data', (data) => {
        const output = data.toString();
        stderr += output;
        this.logger.log(output.trim());
      });

      process.on('close', (code) => {
        if (code === 0) {
          this.logger.log('Dependencies installed successfully');
          resolve({ 
            success: true, 
            stdout, 
            stderr,
            packagesInstalled: totalPackages
          });
        } else {
          this.logger.error(`Pip install failed with code ${code}`);
          this.logger.error('stderr:', stderr);
          reject(new Error(`Dependency installation failed with code ${code}\n${stderr}`));
        }
      });

      process.on('error', (error) => {
        this.logger.error('Pip process error:', error);
        reject(error);
      });
    });
  }

  /**
   * Upgrade pip itself
   */
  async upgradePip() {
    this.logger.log('Upgrading pip...');

    return new Promise((resolve, reject) => {
      const process = spawn(this.pythonPath, [
        '-m', 'pip', 'install', '--upgrade', 'pip', '--no-warn-script-location', '--disable-pip-version-check'
      ], {
        shell: true,
        windowsHide: false,
        env: {
          ...process.env,
          PYTHONIOENCODING: 'utf-8',
          PYTHONUNBUFFERED: '1'
        }
      });

      let output = '';

      process.stdout.on('data', (data) => {
        output += data.toString();
        this.logger.log(data.toString().trim());
      });

      process.stderr.on('data', (data) => {
        output += data.toString();
        this.logger.log(data.toString().trim());
      });

      process.on('close', (code) => {
        if (code === 0) {
          this.logger.log('Pip upgraded successfully');
          resolve({ success: true, output });
        } else {
          // Pip upgrade failure is not critical
          this.logger.warn('Pip upgrade failed, but continuing...');
          resolve({ success: false, output });
        }
      });

      process.on('error', (error) => {
        this.logger.warn('Pip upgrade error:', error);
        resolve({ success: false, error: error.message });
      });
    });
  }

  /**
   * Install single package
   */
  async installPackage(packageName, version = null) {
    const packageSpec = version ? `${packageName}${version}` : packageName;
    this.logger.log(`Installing package: ${packageSpec}`);

    return new Promise((resolve, reject) => {
      const process = spawn(this.pythonPath, [
        '-m', 'pip', 'install', packageSpec
      ], {
        shell: true,
        windowsHide: true
      });

      let output = '';

      process.stdout.on('data', (data) => {
        output += data.toString();
        this.logger.log(data.toString().trim());
      });

      process.stderr.on('data', (data) => {
        output += data.toString();
        this.logger.log(data.toString().trim());
      });

      process.on('close', (code) => {
        if (code === 0) {
          resolve({ success: true, output });
        } else {
          reject(new Error(`Failed to install ${packageSpec}: ${output}`));
        }
      });

      process.on('error', reject);
    });
  }

  /**
   * List installed packages
   */
  async listInstalled() {
    return new Promise((resolve, reject) => {
      const process = spawn(this.pythonPath, ['-m', 'pip', 'list'], {
        shell: true,
        windowsHide: true
      });

      let output = '';

      process.stdout.on('data', (data) => {
        output += data.toString();
      });

      process.on('close', (code) => {
        if (code === 0) {
          const packages = output
            .split('\n')
            .slice(2) // Skip header lines
            .map(line => {
              const parts = line.trim().split(/\s+/);
              return parts.length >= 2 ? { name: parts[0], version: parts[1] } : null;
            })
            .filter(pkg => pkg !== null);
          
          resolve(packages);
        } else {
          reject(new Error('Failed to list packages'));
        }
      });

      process.on('error', reject);
    });
  }
}

module.exports = DependencyInstaller;
