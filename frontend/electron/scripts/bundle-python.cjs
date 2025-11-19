/**
 * Bundle Python Script
 * Downloads Python embedded and installs all dependencies
 * This runs ONCE on dev machine to create the bundle
 */

const https = require('https');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

class PythonBundler {
  constructor() {
    this.projectRoot = path.join(__dirname, '../../../');
    this.bundleDir = path.join(__dirname, '../resources/python-bundle');
    this.pythonDir = path.join(this.bundleDir, 'python-embedded');
    this.backendDir = path.join(this.projectRoot, 'backend');
    this.pythonZip = path.join(this.bundleDir, 'python.zip');
    this.pythonUrl = 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip';
  }

  async bundle() {
    console.log('🔨 Starting Python bundling process...\n');

    try {
      // Step 1: Download Python
      if (!fs.existsSync(this.pythonDir)) {
        await this.downloadPython();
        await this.extractPython();
      } else {
        console.log('✅ Python already downloaded');
      }

      // Step 2: Configure Python for pip
      await this.configurePython();

      // Step 3: Install pip
      await this.installPip();

      // Step 4: Install all dependencies
      await this.installDependencies();

      // Step 5: Verify installation
      await this.verify();

      console.log('\n✅ Python bundle created successfully!');
      console.log(`📁 Location: ${this.pythonDir}`);
      console.log(`📦 Size: ${this.getDirectorySize(this.pythonDir)} MB`);

    } catch (error) {
      console.error('❌ Bundling failed:', error);
      throw error;
    }
  }

  async downloadPython() {
    console.log('📥 Downloading Python 3.11.9 embedded...');

    return new Promise((resolve, reject) => {
      const file = fs.createWriteStream(this.pythonZip);

      https.get(this.pythonUrl, (response) => {
        if (response.statusCode !== 200) {
          reject(new Error(`Download failed: HTTP ${response.statusCode}`));
          return;
        }

        const totalSize = parseInt(response.headers['content-length'], 10);
        let downloadedSize = 0;

        response.on('data', (chunk) => {
          downloadedSize += chunk.length;
          const percent = Math.round((downloadedSize / totalSize) * 100);
          process.stdout.write(`\r   Progress: ${percent}% (${Math.round(downloadedSize / 1024 / 1024)} MB / ${Math.round(totalSize / 1024 / 1024)} MB)`);
        });

        response.pipe(file);

        file.on('finish', () => {
          file.close();
          console.log('\n✅ Download complete');
          resolve();
        });

      }).on('error', (err) => {
        fs.unlink(this.pythonZip, () => {});
        reject(err);
      });
    });
  }

  async extractPython() {
    console.log('📦 Extracting Python...');

    // Use AdmZip for reliable extraction
    const AdmZip = require('adm-zip');

    try {
      const zip = new AdmZip(this.pythonZip);
      zip.extractAllTo(this.pythonDir, true);

      // Clean up zip file
      fs.unlinkSync(this.pythonZip);

      console.log('✅ Extraction complete');
    } catch (error) {
      throw new Error(`Extraction failed: ${error.message}`);
    }
  }

  async configurePython() {
    console.log('⚙️  Configuring Python for pip...');

    const pthFile = path.join(this.pythonDir, 'python311._pth');

    if (fs.existsSync(pthFile)) {
      let content = fs.readFileSync(pthFile, 'utf8');

      if (content.includes('#import site')) {
        content = content.replace('#import site', 'import site');
      } else if (!content.includes('import site')) {
        content += '\nimport site\n';
      }

      fs.writeFileSync(pthFile, content, 'utf8');
      console.log('✅ python311._pth configured');
    }

    // Create Scripts directory
    const scriptsDir = path.join(this.pythonDir, 'Scripts');
    if (!fs.existsSync(scriptsDir)) {
      fs.mkdirSync(scriptsDir, { recursive: true });
      console.log('✅ Scripts directory created');
    }
  }

  async installPip() {
    console.log('📦 Installing pip...');

    // Download get-pip.py
    const getPipUrl = 'https://bootstrap.pypa.io/get-pip.py';
    const getPipPath = path.join(this.pythonDir, 'get-pip.py');

    await new Promise((resolve, reject) => {
      const file = fs.createWriteStream(getPipPath);

      https.get(getPipUrl, (response) => {
        if (response.statusCode !== 200) {
          reject(new Error(`Download failed: HTTP ${response.statusCode}`));
          return;
        }

        response.pipe(file);
        file.on('finish', () => {
          file.close();
          resolve();
        });
      }).on('error', reject);
    });

    console.log('✅ get-pip.py downloaded');

    // Run get-pip.py
    await this.runPython([getPipPath, '--no-warn-script-location']);
    console.log('✅ Pip installed');
  }

  async installDependencies() {
    console.log('📦 Installing Django dependencies...');

    const requirementsFile = path.join(this.backendDir, 'requirements.txt');

    if (!fs.existsSync(requirementsFile)) {
      throw new Error('requirements.txt not found');
    }

    console.log(`   Reading: ${requirementsFile}`);

    await this.runPython([
      '-m', 'pip', 'install',
      '-r', requirementsFile,
      '--no-cache-dir',
      '--no-warn-script-location',
      '--disable-pip-version-check'
    ]);

    console.log('✅ All dependencies installed');
  }

  async verify() {
    console.log('🔍 Verifying installation...');

    const pythonExe = path.join(this.pythonDir, 'python.exe');

    // Check Python version
    await this.runPython(['--version']);

    // Check pip
    await this.runPython(['-m', 'pip', '--version']);

    // Check Django
    await this.runPython(['-m', 'pip', 'show', 'django']);

    console.log('✅ Verification complete');
  }

  async runPython(args) {
    const pythonExe = path.join(this.pythonDir, 'python.exe');

    return new Promise((resolve, reject) => {
      const pythonProcess = spawn(pythonExe, args, {
        shell: true,
        env: {
          ...process.env,
          PYTHONIOENCODING: 'utf-8',
          PYTHONUNBUFFERED: '1'
        }
      });

      let output = '';

      pythonProcess.stdout.on('data', (data) => {
        output += data.toString();
        process.stdout.write(data);
      });

      pythonProcess.stderr.on('data', (data) => {
        output += data.toString();
        process.stderr.write(data);
      });

      pythonProcess.on('close', (code) => {
        if (code === 0) {
          resolve(output);
        } else {
          reject(new Error(`Command failed with code ${code}`));
        }
      });

      pythonProcess.on('error', reject);
    });
  }

  getDirectorySize(dirPath) {
    let totalSize = 0;

    const files = fs.readdirSync(dirPath, { withFileTypes: true });

    for (const file of files) {
      const filePath = path.join(dirPath, file.name);

      if (file.isDirectory()) {
        totalSize += this.getDirectorySize(filePath);
      } else {
        totalSize += fs.statSync(filePath).size;
      }
    }

    return (totalSize / 1024 / 1024).toFixed(2);
  }
}

// Run bundler
const bundler = new PythonBundler();
bundler.bundle().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
