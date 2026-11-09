import { QueuedWriteError } from './offlineManager'

export const isQueuedWrite = (e: unknown): e is QueuedWriteError => e instanceof QueuedWriteError

export const acceptQueued = async <T>(write: () => Promise<T>): Promise<T | undefined> => {
  try {
    return await write()
  } catch (e) {
    if (!isQueuedWrite(e)) throw e
  }
}
