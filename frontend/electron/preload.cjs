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
  getSetupState: () => ipcRenderer.invoke('get-setup-state'),
  resetSetup: () => ipcRenderer.invoke('reset-setup'),
  startSetup: () => ipcRenderer.invoke('start-setup'),
  checkSetupStatus: (step) => ipcRenderer.invoke('check-setup-status', step),
  completeSetup: () => {
    console.log('Preload: Sending setup-complete event');
    ipcRenderer.send('setup-complete');
  },
  
  // Offline/Sync management
  getSyncQueue: () => ipcRenderer.invoke('get-sync-queue'),
  clearSyncQueue: () => ipcRenderer.invoke('clear-sync-queue'),
  
  // App info
  platform: process.platform,
  version: process.versions.electron
});
