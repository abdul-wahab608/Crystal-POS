"""
Script to build Django backend into a standalone executable using PyInstaller.
This creates a bundled version of the backend that can be distributed with the Electron app.
"""

import PyInstaller.__main__
import os
import sys

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# PyInstaller configuration
PyInstaller.__main__.run([
    'manage.py',  # Entry point
    '--name=crystal-backend',  # Output name
    '--onefile',  # Single executable file
    '--console',  # Show console (useful for debugging)
    '--noconfirm',  # Overwrite output directory without asking
    
    # Add all Django apps and their dependencies
    '--hidden-import=django',
    '--hidden-import=rest_framework',
    '--hidden-import=corsheaders',
    '--hidden-import=rest_framework_simplejwt',
    '--hidden-import=django_filters',
    
    # Add all project apps
    '--hidden-import=users',
    '--hidden-import=customers',
    '--hidden-import=vendors',
    '--hidden-import=products',
    '--hidden-import=raw_materials',
    '--hidden-import=sales',
    '--hidden-import=purchases',
    '--hidden-import=assets',
    '--hidden-import=payments',
    '--hidden-import=reports',
    '--hidden-import=bank_accounts',
    
    # Add Django template and static files
    '--collect-data=django',
    '--collect-submodules=django',
    
    # Output directory
    f'--distpath={os.path.join(BASE_DIR, "dist")}',
    f'--workpath={os.path.join(BASE_DIR, "build")}',
    f'--specpath={os.path.join(BASE_DIR, "build")}',
])

print("\n✅ Backend build complete!")
print(f"Executable location: {os.path.join(BASE_DIR, 'dist', 'crystal-backend.exe')}")
