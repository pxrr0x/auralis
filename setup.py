"""
Auralis - Command-Line Music & Playlist Downloader
CS50x Final Project - Harvard University

Author: Prince Addai Desmond | pxrr0x
Date: May 30 2026
"""

import os
import sys
import subprocess

def run_command(command, shell=False):
    """Safely runs system commands and prints output."""
    try:
        subprocess.check_call(command, shell=shell)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Error executing command: {command}\nDetails: {e}")
        return False

def setup_desktop():
    """Installation procedure for Windows, Ubuntu, and macOS."""
    print("\n--- Auralis Desktop Environment Setup ---")
    
    # Check if requirements.txt exists in the current directory
    if os.path.exists("requirements.txt"):
        print("[*] Installing Python dependencies from requirements.txt...")
        success = run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    else:
        print("[!] requirements.txt not found! Installing fallback core packages...")
        dependencies = ["ytmusicapi", "yt-dlp", "syncedlyrics", "mutagen"]
        success = run_command([sys.executable, "-m", "pip", "install"] + dependencies)
        
    if success:
        print("\n[✓] Python dependencies installed successfully!")
        print("[i] Note: Please ensure 'ffmpeg' is installed and added to your system PATH.")
        print("    - Windows: 'winget install Gyan.FFmpeg'")
        print("    - Ubuntu/Linux: 'sudo apt install ffmpeg'")

def setup_termux():
    """Installation procedure for Android via Termux emulator environments."""
    print("\n--- Auralis Android / Termux Environment Setup ---")
    
    # 1. Request Android Storage Access Linkage
    print("[*] Requesting Android shared storage permissions...")
    print("    (Please tap 'Allow' on your device screen if prompted)")
    run_command(["termux-setup-storage"])
    
    # 2. Update Termux Packages Repository
    print("[*] Updating system package definitions...")
    run_command(["pkg", "update", "-y"])
    
    # 3. Install Core System Binaries (Python and FFmpeg)
    print("[*] Installing system dependencies (python, ffmpeg)...")
    run_command(["pkg", "install", "python", "ffmpeg", "-y"])
    
    # 4. Install Python Modules via Pip Sequentially for Stability
    print("[*] Ingesting Python application modules...")
    dependencies = ["ytmusicapi", "yt-dlp", "syncedlyrics", "mutagen"]
    
    # Install wheel first to speed up packaging binaries on mobile chip architectures
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "wheel"])
    
    success = True
    for package in dependencies:
        print(f"    -> Deploying: {package}")
        if not run_command([sys.executable, "-m", "pip", "install", package]):
            success = False
            
    if success:
        print("\n[✓] Auralis environment configuration complete inside Termux!")
        print("[i] Your downloads folder will be located at: ~/storage/shared/Music/Auralis")

def main():
    print("==================================================")
    print("           Auralis Deployment Setup Utility       ")
    print("==================================================")
    
    # System detection framework
    is_termux = "termux" in sys.prefix or os.path.exists("/data/data/com.termux")
    
    if is_termux:
        setup_termux()
    else:
        setup_desktop()
        
    print("\n==================================================")
    print(" Setup processing finished. Ready for launch!   ")
    print("==================================================")

if __name__ == "__main__":
    main()