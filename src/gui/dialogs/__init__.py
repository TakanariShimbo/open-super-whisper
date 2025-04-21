"""
ダイアログモジュールのパッケージ初期化ファイル

アプリケーションで使用される各種ダイアログウィンドウを提供します
"""

from src.gui.dialogs.api_key_dialog import APIKeyDialog
from src.gui.dialogs.vocabulary_dialog import VocabularyDialog
from src.gui.dialogs.system_instructions_dialog import SystemInstructionsDialog
from src.gui.dialogs.hotkey_dialog import HotkeyDialog

__all__ = [
    'APIKeyDialog',
    'VocabularyDialog',
    'SystemInstructionsDialog',
    'HotkeyDialog',
] 