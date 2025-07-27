#!/usr/bin/env python3
"""
Setup script for C2 Game Zone Flask Application
This script helps initialize the application and check dependencies.
"""

import os
import sys
import subprocess
import importlib

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'werkzeug'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies!")
        return False

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        'static',
        'static/images',
        'templates'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")

def check_database():
    """Check if database file exists."""
    db_file = 'c2_game_zone.db'
    if os.path.exists(db_file):
        print(f"✅ Database file exists: {db_file}")
    else:
        print(f"📄 Database will be created on first run: {db_file}")

def main():
    """Main setup function."""
    print("🎮 C2 Game Zone - Setup Script")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    print("\n🔍 Checking dependencies...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        response = input("Would you like to install them now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            if not install_dependencies():
                sys.exit(1)
        else:
            print("Please install the missing packages manually:")
            print("pip install -r requirements.txt")
            sys.exit(1)
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Check database
    print("\n🗄️ Checking database...")
    check_database()
    
    print("\n" + "=" * 40)
    print("✅ Setup completed successfully!")
    print("\n🚀 To start the application:")
    print("   python app.py")
    print("\n🌐 Then open your browser to:")
    print("   http://localhost:5000")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main() 