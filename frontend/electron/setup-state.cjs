const fs = require('fs');
const path = require('path');

/**
 * Setup State Manager
 * Tracks the progress and completion of first-time setup
 */

class SetupStateManager {
  constructor(userDataPath) {
    this.userDataPath = userDataPath;
    this.setupStatePath = path.join(userDataPath, '.setup_state.json');
    this.setupCompletePath = path.join(userDataPath, '.setup_complete');
    this.state = this.loadState();
  }

  /**
   * Load setup state from disk
   */
  loadState() {
    try {
      if (fs.existsSync(this.setupStatePath)) {
        const data = fs.readFileSync(this.setupStatePath, 'utf8');
        return JSON.parse(data);
      }
    } catch (error) {
      console.error('Error loading setup state:', error);
    }

    // Default state
    return {
      version: '1.0.0',
      setupComplete: false,
      steps: {
        python: { status: 'pending', completedAt: null, error: null },
        dependencies: { status: 'pending', completedAt: null, error: null },
        database: { status: 'pending', completedAt: null, error: null },
        admin: { status: 'pending', completedAt: null, error: null }
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
  }

  /**
   * Save setup state to disk
   */
  saveState() {
    try {
      this.state.updatedAt = new Date().toISOString();
      
      // Ensure directory exists
      if (!fs.existsSync(this.userDataPath)) {
        fs.mkdirSync(this.userDataPath, { recursive: true });
      }

      fs.writeFileSync(
        this.setupStatePath, 
        JSON.stringify(this.state, null, 2),
        'utf8'
      );
    } catch (error) {
      console.error('Error saving setup state:', error);
      throw error;
    }
  }

  /**
   * Check if setup is complete
   */
  isSetupComplete() {
    // Check for old flag file
    if (fs.existsSync(this.setupCompletePath)) {
      return true;
    }

    // Check state
    return this.state.setupComplete === true;
  }

  /**
   * Check if first run (no setup ever started)
   */
  isFirstRun() {
    return !fs.existsSync(this.setupStatePath) && 
           !fs.existsSync(this.setupCompletePath);
  }

  /**
   * Update step status
   */
  updateStep(stepName, status, error = null) {
    if (!this.state.steps[stepName]) {
      throw new Error(`Invalid step name: ${stepName}`);
    }

    this.state.steps[stepName].status = status;
    this.state.steps[stepName].error = error;

    if (status === 'complete') {
      this.state.steps[stepName].completedAt = new Date().toISOString();
    }

    this.saveState();
    console.log(`Setup step updated: ${stepName} -> ${status}`);
  }

  /**
   * Get step status
   */
  getStepStatus(stepName) {
    return this.state.steps[stepName] || null;
  }

  /**
   * Mark entire setup as complete
   */
  markComplete(version) {
    this.state.setupComplete = true;
    this.state.completedAt = new Date().toISOString();
    this.state.version = version || this.state.version;
    
    // Mark all steps as complete if not already
    Object.keys(this.state.steps).forEach(stepName => {
      if (this.state.steps[stepName].status !== 'complete') {
        this.state.steps[stepName].status = 'complete';
        this.state.steps[stepName].completedAt = new Date().toISOString();
      }
    });

    this.saveState();

    // Also create the old flag file for compatibility
    try {
      fs.writeFileSync(this.setupCompletePath, JSON.stringify({
        completedAt: new Date().toISOString(),
        version: version || this.state.version
      }));
    } catch (error) {
      console.error('Error creating setup complete flag:', error);
    }

    console.log('Setup marked as complete!');
  }

  /**
   * Reset setup state (for testing)
   */
  reset() {
    // Delete state file
    if (fs.existsSync(this.setupStatePath)) {
      fs.unlinkSync(this.setupStatePath);
    }

    // Delete old flag file
    if (fs.existsSync(this.setupCompletePath)) {
      fs.unlinkSync(this.setupCompletePath);
    }

    // Reset in-memory state
    this.state = {
      version: '1.0.0',
      setupComplete: false,
      steps: {
        python: { status: 'pending', completedAt: null, error: null },
        dependencies: { status: 'pending', completedAt: null, error: null },
        database: { status: 'pending', completedAt: null, error: null },
        admin: { status: 'pending', completedAt: null, error: null }
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    console.log('Setup state reset!');
  }

  /**
   * Get full state object
   */
  getState() {
    return { ...this.state };
  }

  /**
   * Get setup progress percentage
   */
  getProgress() {
    const steps = Object.values(this.state.steps);
    const completed = steps.filter(s => s.status === 'complete').length;
    return Math.round((completed / steps.length) * 100);
  }
}

module.exports = SetupStateManager;
