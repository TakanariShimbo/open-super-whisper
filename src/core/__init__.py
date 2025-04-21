"""
コアモジュール

アプリケーションの中核となる機能を提供します。
"""

from src.core.whisper_api import WhisperTranscriber
from src.core.audio_recorder import AudioRecorder
from src.core.hotkeys import HotkeyManager

__all__ = ["WhisperTranscriber", "AudioRecorder", "HotkeyManager"]
