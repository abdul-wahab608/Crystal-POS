/**
 * Pre-build script to prepare the app for production build
 */

const fs = require('fs');
const path = require('path');

console.log('🔨 Running pre-build checks...');

// Base directory is frontend/
const frontendDir = path.join(__dirname, '..');

// Check if backend folder exists
const backendPath = path.join(frontendDir, '..', 'backend');
if (!fs.existsSync(backendPath)) {
  console.error('❌ Error: backend/ folder not found.');
  process.exit(1);
}

// Check if db.sqlite3 exists
const dbPath = path.join(backendPath, 'db.sqlite3');
if (!fs.existsSync(dbPath)) {
  console.warn('⚠️ Warning: db.sqlite3 not found. A fresh database will be created on first run.');
}

// Check electron folder
const electronPath = path.join(frontendDir, 'electron');
if (!fs.existsSync(electronPath)) {
  console.error('❌ Error: electron/ folder not found.');
  process.exit(1);
}

// Verify critical files
const criticalFiles = [
  'electron/main.cjs',
  'electron/preload.cjs',
  'electron/setup.html',
  'electron/port-utils.cjs'
];

let allFilesExist = true;
criticalFiles.forEach(file => {
  const filePath = path.join(frontendDir, file);
  if (!fs.existsSync(filePath)) {
    console.error(`❌ Error: ${file} not found.`);
    allFilesExist = false;
  }
});

if (!allFilesExist) {
  process.exit(1);
}

console.log('✅ All pre-build checks passed!');
console.log('📦 Ready to build installer...');
