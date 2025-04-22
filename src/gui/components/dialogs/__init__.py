"""
ダイアログコンポーネントのパッケージ

アプリケーションで使用される各種ダイアログを提供します。
"""

from src.gui.components.dialogs.api_key_dialog import APIKeyDialog
# 以下は指示セットダイアログに統合されましたが、コードは参照用に残します
# from src.gui.components.dialogs.vocabulary_dialog import VocabularyDialog
# from src.gui.components.dialogs.system_instructions_dialog import SystemInstructionsDialog
from src.gui.components.dialogs.hotkey_dialog import HotkeyDialog
from src.gui.components.dialogs.instruction_sets_dialog import InstructionSetsDialog
from src.gui.components.dialogs.simple_input_dialog import SimpleInputDialog
from src.gui.components.dialogs.simple_message_dialog import SimpleMessageDialog 