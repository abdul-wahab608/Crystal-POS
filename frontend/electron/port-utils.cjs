/**
 * Utility to find an available port dynamically
 */
const net = require('net');

function checkPort(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    
    server.once('error', (err) => {
      if (err.code === 'EADDRINUSE') {
        resolve(false); // Port is in use
      } else {
        resolve(false);
      }
    });
    
    server.once('listening', () => {
      server.close();
      resolve(true); // Port is available
    });
    
    server.listen(port, '127.0.0.1');
  });
}

async function findAvailablePort(startPort = 8000, maxAttempts = 10) {
  for (let i = 0; i < maxAttempts; i++) {
    const port = startPort + i;
    const available = await checkPort(port);
    
    if (available) {
      return port;
    }
  }
  
  throw new Error(`No available port found in range ${startPort}-${startPort + maxAttempts - 1}`);
}

module.exports = {
  checkPort,
  findAvailablePort
};
