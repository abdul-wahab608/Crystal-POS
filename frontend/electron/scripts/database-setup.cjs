const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * Database Setup Module
 * Handles Django migrations and admin user creation
 */

class DatabaseSetup {
  constructor(pythonPath, backendPath, dbPath, logger = console) {
    this.pythonPath = pythonPath;
    this.backendPath = backendPath;
    this.dbPath = dbPath;
    this.logger = logger;
    this.managePyPath = path.join(backendPath, 'manage.py');
  }

  /**
   * Check if manage.py exists
   */
  managePyExists() {
    return fs.existsSync(this.managePyPath);
  }

  /**
   * Check if database file exists
   */
  databaseExists() {
    return fs.existsSync(this.dbPath);
  }

  /**
   * Run Django management command
   */
  async runManageCommand(args, env = {}) {
    return new Promise((resolve, reject) => {
      const fullEnv = {
        ...process.env,
        DJANGO_DB_PATH: this.dbPath,
        DJANGO_SECRET_KEY: 'desktop-app-secret-key-' + Date.now(),
        PYTHONPATH: this.backendPath,
        ...env
      };

      this.logger.log('Running Django command:', this.pythonPath, this.managePyPath, args.join(' '));
      this.logger.log('Database path:', this.dbPath);

      const process = spawn(this.pythonPath, [this.managePyPath, ...args], {
        cwd: this.backendPath,
        env: fullEnv,
        shell: true,
        windowsHide: true
      });

      let stdout = '';
      let stderr = '';

      process.stdout.on('data', (data) => {
        const output = data.toString();
        stdout += output;
        this.logger.log(output.trim());
      });

      process.stderr.on('data', (data) => {
        const output = data.toString();
        stderr += output;
        this.logger.log(output.trim());
      });

      process.on('close', (code) => {
        if (code === 0) {
          resolve({ success: true, stdout, stderr, code });
        } else {
          reject(new Error(`Django command failed with code ${code}\n${stderr}`));
        }
      });

      process.on('error', (error) => {
        reject(error);
      });
    });
  }

  /**
   * Check if migrations are needed
   */
  async checkMigrations() {
    try {
      this.logger.log('Checking migration status...');
      
      // Run showmigrations to see what's pending
      const result = await this.runManageCommand(['showmigrations', '--plan']);
      
      // Check if there are any [ ] (unapplied) migrations
      const hasUnapplied = result.stdout.includes('[ ]');
      
      this.logger.log(`Migrations needed: ${hasUnapplied}`);
      return hasUnapplied;

    } catch (error) {
      // If showmigrations fails, database probably doesn't exist yet
      this.logger.log('Migration check failed (database may not exist)');
      return true;
    }
  }

  /**
   * Run database migrations
   */
  async migrate(onProgress = null) {
    this.logger.log('Running database migrations...');

    if (!this.managePyExists()) {
      throw new Error('manage.py not found at: ' + this.managePyPath);
    }

    // Ensure database directory exists
    const dbDir = path.dirname(this.dbPath);
    if (!fs.existsSync(dbDir)) {
      fs.mkdirSync(dbDir, { recursive: true });
      this.logger.log('Created database directory:', dbDir);
    }

    try {
      if (onProgress) onProgress('checking', 0);

      // Check if migrations are needed
      const needsMigrations = await this.checkMigrations();
      
      if (!needsMigrations && this.databaseExists()) {
        this.logger.log('Database is up to date, no migrations needed');
        return { success: true, message: 'No migrations needed', migrated: false };
      }

      if (onProgress) onProgress('migrating', 50);

      // Run migrations
      const result = await this.runManageCommand(['migrate', '--noinput']);

      this.logger.log('Migrations completed successfully');
      
      return {
        success: true,
        message: 'Migrations applied successfully',
        migrated: true,
        output: result.stdout
      };

    } catch (error) {
      this.logger.error('Migration failed:', error);
      throw error;
    }
  }

  /**
   * Check if admin user exists
   */
  async adminExists(username = 'admin') {
    try {
      this.logger.log(`Checking if admin user '${username}' exists...`);

      const shellCommand = `from users.models import User; exists = User.objects.filter(username='${username}').exists(); print('EXISTS' if exists else 'NOT_EXISTS')`;
      
      const result = await this.runManageCommand(['shell', '-c', shellCommand]);
      
      const exists = result.stdout.includes('EXISTS');
      this.logger.log(`Admin user exists: ${exists}`);
      
      return exists;

    } catch (error) {
      this.logger.error('Error checking admin user:', error);
      return false;
    }
  }

  /**
   * Create admin user
   */
  async createAdmin(username = 'admin', password = 'admin123', email = 'admin@crystal.com') {
    this.logger.log('Creating admin user...');

    if (!this.managePyExists()) {
      throw new Error('manage.py not found');
    }

    try {
      // Check if admin already exists
      const exists = await this.adminExists(username);
      
      if (exists) {
        this.logger.log('Admin user already exists');
        return { 
          success: true, 
          message: 'Admin user already exists',
          created: false,
          username 
        };
      }

      // Create superuser
      this.logger.log(`Creating superuser: ${username}`);
      
      await this.runManageCommand([
        'createsuperuser',
        '--noinput',
        '--username', username,
        '--email', email
      ]);

      // Set password using shell command
      const shellCommand = `from users.models import User; u = User.objects.get(username='${username}'); u.set_password('${password}'); u.save(); print('Password set successfully')`;
      
      await this.runManageCommand(['shell', '-c', shellCommand]);

      this.logger.log(`Admin user created: ${username} / ${password}`);

      return {
        success: true,
        message: 'Admin user created successfully',
        created: true,
        username,
        password
      };

    } catch (error) {
      this.logger.error('Failed to create admin user:', error);
      throw error;
    }
  }

  /**
   * Run full database setup (migrate + create admin)
   */
  async setup(adminUsername = 'admin', adminPassword = 'admin123', onProgress = null) {
    this.logger.log('Starting full database setup...');

    try {
      // Step 1: Run migrations
      if (onProgress) onProgress('migrations', 0);
      const migrateResult = await this.migrate((status, progress) => {
        if (onProgress) onProgress('migrations', progress);
      });

      // Step 2: Create admin user
      if (onProgress) onProgress('admin', 50);
      const adminResult = await this.createAdmin(adminUsername, adminPassword);

      if (onProgress) onProgress('complete', 100);

      return {
        success: true,
        migrations: migrateResult,
        admin: adminResult
      };

    } catch (error) {
      this.logger.error('Database setup failed:', error);
      throw error;
    }
  }

  /**
   * Verify database is working
   */
  async verify() {
    try {
      this.logger.log('Verifying database...');
      
      // Run check command
      const result = await this.runManageCommand(['check']);
      
      this.logger.log('Database verification successful');
      return { success: true, output: result.stdout };

    } catch (error) {
      this.logger.error('Database verification failed:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Get database info
   */
  getDatabaseInfo() {
    return {
      exists: this.databaseExists(),
      path: this.dbPath,
      size: this.databaseExists() ? fs.statSync(this.dbPath).size : 0
    };
  }
}

module.exports = DatabaseSetup;
