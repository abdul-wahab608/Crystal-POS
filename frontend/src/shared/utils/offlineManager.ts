/**
 * Offline Manager - Handles network detection and offline mode
 */

class OfflineManager {
  constructor() {
    this.isOnline = navigator.onLine;
    this.listeners = new Set();
    this.syncQueue = [];
    
    // Setup event listeners
    window.addEventListener('online', () => this.handleOnline());
    window.addEventListener('offline', () => this.handleOffline());
    
    // Load sync queue from localStorage
    this.loadSyncQueue();
  }

  /**
   * Check if currently online
   */
  checkOnlineStatus() {
    return this.isOnline;
  }

  /**
   * Handle going online
   */
  handleOnline() {
    console.log('🟢 Network connection restored');
    this.isOnline = true;
    this.notifyListeners({ online: true });
    
    // Process sync queue
    this.processSyncQueue();
  }

  /**
   * Handle going offline
   */
  handleOffline() {
    console.log('🔴 Network connection lost - Offline mode enabled');
    this.isOnline = false;
    this.notifyListeners({ online: false });
  }

  /**
   * Subscribe to network status changes
   */
  subscribe(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  /**
   * Notify all listeners
   */
  notifyListeners(status) {
    this.listeners.forEach(callback => callback(status));
  }

  /**
   * Add request to sync queue
   */
  addToSyncQueue(request) {
    const queueItem = {
      id: Date.now() + Math.random(),
      timestamp: new Date().toISOString(),
      method: request.method,
      url: request.url,
      data: request.data,
      retries: 0,
      maxRetries: 3
    };
    
    this.syncQueue.push(queueItem);
    this.saveSyncQueue();
    
    console.log('📥 Added to sync queue:', queueItem);
    return queueItem.id;
  }

  /**
   * Remove item from sync queue
   */
  removeFromSyncQueue(id) {
    this.syncQueue = this.syncQueue.filter(item => item.id !== id);
    this.saveSyncQueue();
  }

  /**
   * Process sync queue when back online
   */
  async processSyncQueue() {
    if (!this.isOnline || this.syncQueue.length === 0) {
      return;
    }

    console.log(`📤 Processing ${this.syncQueue.length} queued requests...`);

    const queue = [...this.syncQueue];
    
    for (const item of queue) {
      try {
        // Attempt to sync
        const response = await fetch(item.url, {
          method: item.method,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: item.data ? JSON.stringify(item.data) : undefined
        });

        if (response.ok) {
          console.log('✅ Synced:', item.url);
          this.removeFromSyncQueue(item.id);
        } else {
          throw new Error(`Sync failed with status ${response.status}`);
        }
      } catch (error) {
        console.error('❌ Sync failed:', item.url, error);
        
        item.retries++;
        if (item.retries >= item.maxRetries) {
          console.error('🚫 Max retries reached, removing from queue:', item.url);
          this.removeFromSyncQueue(item.id);
        } else {
          this.saveSyncQueue();
        }
      }
    }
  }

  /**
   * Save sync queue to localStorage
   */
  saveSyncQueue() {
    try {
      localStorage.setItem('offline_sync_queue', JSON.stringify(this.syncQueue));
    } catch (error) {
      console.error('Failed to save sync queue:', error);
    }
  }

  /**
   * Load sync queue from localStorage
   */
  loadSyncQueue() {
    try {
      const saved = localStorage.getItem('offline_sync_queue');
      if (saved) {
        this.syncQueue = JSON.parse(saved);
        console.log(`📦 Loaded ${this.syncQueue.length} items from sync queue`);
      }
    } catch (error) {
      console.error('Failed to load sync queue:', error);
      this.syncQueue = [];
    }
  }

  /**
   * Get sync queue status
   */
  getSyncQueueStatus() {
    return {
      total: this.syncQueue.length,
      items: this.syncQueue
    };
  }

  /**
   * Clear sync queue
   */
  clearSyncQueue() {
    this.syncQueue = [];
    this.saveSyncQueue();
    console.log('🗑️ Sync queue cleared');
  }
}

// Create singleton instance
const offlineManager = new OfflineManager();

export default offlineManager;
