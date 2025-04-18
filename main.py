#!/usr/bin/env python3
"""
Open Super Whisper - A Python desktop application for speech transcription
using OpenAI's Whisper model.

This application provides a user-friendly interface for recording audio and
transcribing it using the OpenAI Whisper API. It also supports importing
audio files, custom vocabulary, and various output options.
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the main window
from src.gui.main_window import main

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Open Super Whisper")
    parser.add_argument("-m", "--minimized", action="store_true", 
                        help="Start application minimized to system tray")
    args = parser.parse_args()
    
    # Start the application
    if args.minimized:
        sys.argv.append("--minimized")
    main()
