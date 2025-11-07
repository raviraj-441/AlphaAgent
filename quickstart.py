#!/usr/bin/env python3
"""
Quick start script for tax-loss harvesting backend.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def check_groq_api_key():
    """Check if GROQ_API_KEY is set"""
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  GROQ_API_KEY environment variable not set")
        print("   Set it with: export GROQ_API_KEY='your_key_here'")
        return False
    print("✅ GROQ_API_KEY is set")
    return True


def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            cwd=str(Path(__file__).parent)
        )
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = [
        "./logs",
        "./data/chroma_db",
        "./data/income_tax_law_texts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory}")


def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path(".env")
    env_template = Path(".env.template")
    
    if env_file.exists():
        print("\n✅ .env file already exists")
        return
    
    if env_template.exists():
        print("\n📝 Creating .env file from template...")
        env_file.write_text(env_template.read_text())
        print("✅ .env file created. Please update with your settings.")
    else:
        print("⚠️  .env.template not found")


def run_server():
    """Run the FastAPI server"""
    print("\n🚀 Starting FastAPI server...")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("   Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", 
             "backend.main:app", "--reload",
             "--host", "0.0.0.0", "--port", "8000"],
            cwd=str(Path(__file__).parent)
        )
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")


def main():
    """Main quickstart routine"""
    print("=" * 60)
    print("  Tax-Loss Harvesting Multi-Agent Backend - Quick Start")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check Groq API key
    if not check_groq_api_key():
        print("\n⚠️  Proceeding without GROQ_API_KEY (some features may not work)")
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Start server
    run_server()


if __name__ == "__main__":
    main()
