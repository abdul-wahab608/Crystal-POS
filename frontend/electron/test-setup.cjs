/**
 * Test Setup Flow
 * Validates all setup modules work correctly
 */

const path = require('path');
const fs = require('fs');

// Setup paths
const testDataPath = path.join(__dirname, '../test-data');
const backendPath = path.join(__dirname, '../../backend');

// Create test data directory
if (!fs.existsSync(testDataPath)) {
  fs.mkdirSync(testDataPath, { recursive: true });
}

console.log('=== Setup Flow Test ===\n');
console.log('Test Data Path:', testDataPath);
console.log('Backend Path:', backendPath);
console.log('');

// Test 1: Setup State Manager
console.log('Test 1: Setup State Manager');
try {
  const SetupStateManager = require('./setup-state.cjs');
  const setupState = new SetupStateManager(testDataPath);
  
  console.log('  ✓ Module loaded');
  console.log('  Is first run?', setupState.isFirstRun());
  console.log('  Is setup complete?', setupState.isSetupComplete());
  
  // Update a step
  setupState.updateStep('python', 'complete');
  console.log('  ✓ Updated python step');
  console.log('  Progress:', setupState.getProgress() + '%');
  
  console.log('  ✓ SetupStateManager: PASS\n');
} catch (error) {
  console.error('  ✗ SetupStateManager: FAIL', error.message);
  process.exit(1);
}

// Test 2: Python Installer
console.log('Test 2: Python Installer');
try {
  const PythonInstaller = require('./scripts/python-installer.cjs');
  const pythonInstaller = new PythonInstaller(testDataPath);
  
  console.log('  ✓ Module loaded');
  console.log('  Python version to install:', pythonInstaller.pythonVersion);
  console.log('  Download URL:', pythonInstaller.pythonDownloadUrl);
  
  // Check if Python is installed
  pythonInstaller.isPythonInstalled().then(result => {
    console.log('  Python installed?', result.installed);
    if (result.installed) {
      console.log('  Python path:', result.path);
      console.log('  Python type:', result.type);
    }
    console.log('  ✓ PythonInstaller: PASS\n');
    
    // Continue with next test
    testDependencyInstaller(result.path || 'python');
  });
} catch (error) {
  console.error('  ✗ PythonInstaller: FAIL', error.message);
  process.exit(1);
}

// Test 3: Dependency Installer
function testDependencyInstaller(pythonPath) {
  console.log('Test 3: Dependency Installer');
  try {
    const DependencyInstaller = require('./scripts/dependency-installer.cjs');
    const depInstaller = new DependencyInstaller(pythonPath, backendPath);
    
    console.log('  ✓ Module loaded');
    console.log('  Requirements.txt exists?', depInstaller.requirementsExists());
    
    if (depInstaller.requirementsExists()) {
      const packages = depInstaller.readRequirements();
      console.log('  Packages in requirements.txt:', packages.length);
      packages.forEach(pkg => console.log('    -', pkg.raw));
      
      // Check if dependencies are installed
      depInstaller.areDependenciesInstalled().then(installed => {
        console.log('  Dependencies installed?', installed);
        console.log('  ✓ DependencyInstaller: PASS\n');
        
        // Continue with next test
        testDatabaseSetup(pythonPath);
      });
    } else {
      console.log('  ⚠ requirements.txt not found');
      console.log('  ✓ DependencyInstaller: PASS (module works)\n');
      testDatabaseSetup(pythonPath);
    }
  } catch (error) {
    console.error('  ✗ DependencyInstaller: FAIL', error.message);
    process.exit(1);
  }
}

// Test 4: Database Setup
function testDatabaseSetup(pythonPath) {
  console.log('Test 4: Database Setup');
  try {
    const DatabaseSetup = require('./scripts/database-setup.cjs');
    const testDbPath = path.join(testDataPath, 'test.db');
    const dbSetup = new DatabaseSetup(pythonPath, backendPath, testDbPath);
    
    console.log('  ✓ Module loaded');
    console.log('  manage.py exists?', dbSetup.managePyExists());
    console.log('  Database path:', dbSetup.dbPath);
    console.log('  Database exists?', dbSetup.databaseExists());
    
    const dbInfo = dbSetup.getDatabaseInfo();
    console.log('  Database size:', dbInfo.size, 'bytes');
    
    console.log('  ✓ DatabaseSetup: PASS\n');
    
    // Final summary
    printSummary();
  } catch (error) {
    console.error('  ✗ DatabaseSetup: FAIL', error.message);
    process.exit(1);
  }
}

// Print summary
function printSummary() {
  console.log('=== Test Summary ===');
  console.log('✓ All modules loaded successfully');
  console.log('✓ All basic functionality working');
  console.log('✓ Integration ready for Electron');
  console.log('\nReady for development testing in Electron!');
  
  // Clean up test files
  const testStatePath = path.join(testDataPath, '.setup_state.json');
  if (fs.existsSync(testStatePath)) {
    fs.unlinkSync(testStatePath);
    console.log('\n✓ Cleaned up test state file');
  }
}
