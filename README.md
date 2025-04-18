# Open Super Whisper

A Python-based desktop application for speech transcription using OpenAI's Whisper model.

## Features

- 🎙️ Record audio directly from your microphone
- 📁 Import audio files (supports MP3, WAV, M4A, OGG, FLAC)
- 🌎 Support for 100+ languages with automatic language detection
- 📝 Custom vocabulary support to improve transcription accuracy
- 📋 Copy transcription to clipboard
- 💾 Save transcription to a text file
- 🔄 Real-time recording status and timer

## Requirements

- Python 3.8 or higher
- OpenAI API key
- Windows operating system

## Installation

### Using UV (Fast Package Manager)

[UV](https://github.com/astral-sh/uv) is a fast and efficient Python package installer and environment manager. It's faster than traditional pip and venv, and provides better dependency resolution.

1. Check if UV is installed:

```bash
uv --version
```

2. If not installed, you can install it with:

```bash
# Using pip
pip install uv

# Or using the official method
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Clone or download this repository

4. Set up the project using UV's sync command, which will create a virtual environment and install all dependencies:

```bash
uv sync
```

5. Activate the virtual environment:

```bash
# Windows (Command Prompt)
.venv\Scripts\activate.bat
# Or Windows (PowerShell)
# .\.venv\Scripts\activate.ps1
```

> **Note**: If you get a "execution of scripts is disabled on this system" error when using `activate.ps1` in PowerShell, try one of these solutions:
> 
> 1. Use Command Prompt (cmd.exe) and run `.venv\Scripts\activate.bat` instead
> 2. Run the following command in PowerShell to change the execution policy for the current session only:
>    ```powershell
>    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
>    ```
>    Then run `.\.venv\Scripts\activate.ps1`
> 3. Run PowerShell as Administrator and change the execution policy for your user account (do this only if you understand the security implications):
>    ```powershell
>    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
>    ```

6. Run the application:

```bash
python main.py
```

## Usage

### Setting up your API Key

1. On first launch, you'll be prompted to enter your OpenAI API key
2. If you don't have an API key, you can get one from [OpenAI's website](https://platform.openai.com/api-keys)
3. Your API key will be saved for future use

### Recording Audio

1. Click the "Start Recording" button to begin recording from your microphone
2. Click "Stop Recording" when you're done
3. The application will automatically transcribe your recording

### Importing Audio Files

1. Click the "Import Audio" button
2. Select an audio file from your computer
3. The application will process and transcribe the file

### Language Selection

1. Select a language from the dropdown menu before recording or importing audio
2. Choose "Auto-detect" to let Whisper identify the language automatically

### Custom Vocabulary

1. Click "Custom Vocabulary" in the toolbar
2. Add specific terms, names, or phrases that might appear in your audio
3. These terms will help improve transcription accuracy

### Managing Transcriptions

1. View the transcription in the main text area
2. Edit the text if needed (the text area is editable)
3. Use the toolbar buttons to:
   - Copy the transcription to clipboard
   - Save the transcription as a text file

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- This application uses [OpenAI's Whisper API](https://platform.openai.com/docs/guides/speech-to-text) for speech recognition
- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) for the user interface
- Inspired by the [Super Whisper](https://superwhisper.com/) desktop application
