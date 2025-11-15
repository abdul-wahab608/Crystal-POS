const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // Config management
  getConfig: () => ipcRenderer.invoke('get-config'),
  saveConfig: (config) => ipcRenderer.invoke('save-config', config),
  
  // Path management
  getUserDataPath: () => ipcRenderer.invoke('get-user-data-path'),
  
  // Setup management
  isFirstRun: () => ipcRenderer.invoke('is-first-run'),
  startSetup: () => ipcRenderer.invoke('start-setup'),
  completeSetup: () => ipcRenderer.send('setup-complete'),
  
  // Offline/Sync management
  getSyncQueue: () => ipcRenderer.invoke('get-sync-queue'),
  clearSyncQueue: () => ipcRenderer.invoke('clear-sync-queue'),
  
  // App info
  platform: process.platform,
  version: process.versions.electron
});
