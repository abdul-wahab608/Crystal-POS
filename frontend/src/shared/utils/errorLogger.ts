/**
 * Centralized error logging for production-grade error tracking
 * Logs errors to console and optionally to a persistent log file
 */

interface ErrorContext {
  component?: string
  action?: string
  data?: any
}

class ErrorLogger {
  private errorLog: Array<{ timestamp: string; error: Error; context?: ErrorContext }> = []
  private maxLogSize = 100

  /**
   * Log an error with context
   */
  logError(error: Error, context?: ErrorContext): void {
    const timestamp = new Date().toISOString()
    
    // Add to in-memory log
    this.errorLog.push({ timestamp, error, context })
    
    // Trim log if too large
    if (this.errorLog.length > this.maxLogSize) {
      this.errorLog.shift()
    }

    // Console logging with context
    console.error(`[${timestamp}] Error in ${context?.component || 'Unknown'}:`, {
      message: error.message,
      action: context?.action,
      stack: error.stack,
      data: context?.data
    })

    // In Electron, send to main process for persistent logging
    if ((window as any).electronAPI) {
      this.logToFile(timestamp, error, context)
    }
  }

  /**
   * Log to persistent file in Electron
   */
  private async logToFile(timestamp: string, error: Error, context?: ErrorContext): Promise<void> {
    try {
      // This would require adding an IPC handler in main.cjs
      // For now, just console log that we would persist
      console.log('[ErrorLogger] Would persist to file:', { timestamp, error: error.message, context })
    } catch (e) {
      console.error('Failed to persist error log:', e)
    }
  }

  /**
   * Get recent errors
   */
  getRecentErrors(count = 10): Array<{ timestamp: string; error: Error; context?: ErrorContext }> {
    return this.errorLog.slice(-count)
  }

  /**
   * Clear error log
   */
  clearLog(): void {
    this.errorLog = []
  }
}

// Singleton instance
export const errorLogger = new ErrorLogger()

/**
 * Helper function for wrapping async operations with error logging
 */
export function withErrorLogging<T>(
  operation: () => Promise<T>,
  context: ErrorContext
): Promise<T> {
  return operation().catch((error) => {
    errorLogger.logError(error instanceof Error ? error : new Error(String(error)), context)
    throw error
  })
}
