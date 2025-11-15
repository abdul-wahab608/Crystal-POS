"""
Standalone script to start Django server.
This is used as the entry point for the bundled backend executable.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    # Set up Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    
    # Get database path from environment or use default
    db_path = os.environ.get('DJANGO_DB_PATH', 'db.sqlite3')
    print(f"Using database: {db_path}")
    
    # Get port from environment or use default
    port = os.environ.get('DJANGO_PORT', '8000')
    
    # Start the development server
    sys.argv = ['manage.py', 'runserver', f'127.0.0.1:{port}', '--noreload']
    
    try:
        execute_from_command_line(sys.argv)
    except Exception as e:
        print(f"Error starting Django server: {e}")
        sys.exit(1)
