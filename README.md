# Open Super Whisper

<img src="assets/icon.png" alt="Open Super Whisper Icon" width="128" height="128" align="right"/>

Simple desktop application for speech transcription with global hotkey control. Record, transcribe, and paste - all without switching applications.

## Quick Start - Just 3 Steps!

1. **Start Recording** - Press the global hotkey (default: Ctrl+Shift+R) from any application
2. **Stop Recording** - Press the same hotkey again when you're done speaking
3. **Paste Text** - The transcription is automatically copied to your clipboard, just paste it wherever you need

That's it! No need to switch applications during your workflow.

## Features

- 🎙️ Record audio directly from your microphone
- 🌎 Support for 100+ languages with automatic language detection
- 📝 Custom vocabulary support to improve transcription accuracy
- 🔧 System instructions for controlling transcription behavior
- 📋 Copy transcription to clipboard
- 🔄 Real-time recording status and timer

## Demo

![Demo of Open Super Whisper in action](demo/demo.gif)

## Requirements

- OpenAI API key
- Windows or macOS operating system

## Installation

### Using UV Package Manager

[UV](https://github.com/astral-sh/uv) is a fast and efficient Python package installer and environment manager. It's faster than traditional pip and venv, and provides better dependency resolution.

1. Check if UV is installed:

```bash
uv --version
```

2. If not installed, you can install it with:

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Clone or download this repository

4. Set up the project using UV's sync command, which will create a virtual environment and install all dependencies:

```bash
uv sync
```

5. Activate the virtual environment:

```bash
# Windows (PowerShell)
.\.venv\Scripts\activate.ps1

# macOS/Linux
source .venv/bin/activate
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

### Building the Application

To create a standalone executable, you can use PyInstaller:

```bash
# Windows (PowerShell)
python -m PyInstaller --onefile --windowed --icon assets/icon.ico --name "OpenSuperWhisper" --add-data "assets;assets" main.py

# For macOS
python -m PyInstaller --onefile --windowed --icon assets/icon.icns --name "OpenSuperWhisper" --add-data "assets:assets" main.py

# For Linux
python -m PyInstaller --onefile --windowed --icon assets/linux_pngs/icon_256.png --name "OpenSuperWhisper" --add-data "assets:assets" main.py
```

The Windows command does the following:
- `--onefile`: Creates a single executable file
- `--windowed`: Prevents a console window from appearing
- `--icon assets/icon.ico`: Sets the application icon
- `--name "OpenSuperWhisper"`: Specifies the output filename
- `--add-data "assets;assets"`: Includes the entire assets directory in the executable

Once the build is complete, you'll find `OpenSuperWhisper.exe` in the `dist` folder on Windows, `OpenSuperWhisper.app` in the `dist` folder on macOS, or `OpenSuperWhisper` in the `dist` folder on Linux.

## Usage

### Setting up your API Key

1. On first launch, you'll be prompted to enter your OpenAI API key
2. If you don't have an API key, you can get one from [OpenAI's website](https://platform.openai.com/api-keys)
3. Your API key will be saved for future use
4. To change it later, click "API Key Settings" in the toolbar

### Recording Audio

1. Click the "Start Recording" button to begin recording from your microphone
2. Click "Stop Recording" when you're done
3. The application will automatically transcribe your recording
4. You can also use the global hotkey (default: Ctrl+Shift+R) to start/stop recording even when the application is in the background

### Using Global Hotkeys

1. The default hotkey is set to "Ctrl+Shift+R"
2. Pressing this hotkey will start/stop recording even when the application is in the background
3. To change the hotkey, click "Hotkey Settings" in the toolbar

### Using the System Tray (Windows) or Menu Bar (macOS)

1. The application stays resident in your system tray (Windows) or menu bar (macOS)
2. Closing the window will keep the application running in the background
3. Click the system tray/menu bar icon to toggle the application's visibility
4. Right-click the system tray icon (Windows) or click the menu bar icon (macOS) to access a context menu with options to:
   - Show the application
   - Start/stop recording
   - Completely exit the application

### Language Selection

1. Select a language from the dropdown menu before recording or importing audio
2. Choose "Auto-detect" to let Whisper identify the language automatically

### Model Selection

1. Select the Whisper model to use from the dropdown menu
2. Different models offer different balances of accuracy and processing speed
3. Your selected model will be remembered for future sessions

### Custom Vocabulary

1. Click "Custom Vocabulary" in the toolbar
2. Add specific terms, names, or phrases that might appear in your audio
3. These terms will help improve transcription accuracy

### System Instructions

1. Click "System Instructions" in the toolbar
2. Add specific instructions to control transcription behavior, such as:
   - "Ignore filler words like um, uh, er"
   - "Add proper punctuation"
   - "Format text into paragraphs"
3. These instructions help refine transcription results without manual editing

### Managing Transcriptions

1. View the transcription in the main text area
2. Edit the text if needed (the text area is editable)
3. Use the toolbar buttons to:
   - Copy the transcription to clipboard

### Other Settings

1. "Auto Copy" option: Toggle automatic copying of transcription to clipboard when completed

### Command Line Options

The application supports the following command line arguments:

```bash
python main.py -m
# or
python main.py --minimized
```

Using the `-m` or `--minimized` option will start the application minimized to the system tray only, without showing the window.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- This application uses [OpenAI's Whisper API](https://platform.openai.com/docs/guides/speech-to-text) for speech recognition
- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) for the user interface
- Inspired by the [Super Whisper](https://superwhisper.com/) desktop application
