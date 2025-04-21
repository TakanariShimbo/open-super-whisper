"""
グローバルホットキー設定用のダイアログモジュール

録音の開始/停止に使用するグローバルホットキーを設定するためのダイアログを提供します
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt

from src.gui.resources.labels import AppLabels
from src.gui.resources.styles import AppStyles

class HotkeyDialog(QDialog):
    """
    グローバルホットキー設定を管理するダイアログ
    
    録音の開始/停止に使用するグローバルホットキーを設定するためのダイアログウィンドウ
    """
    
    def __init__(self, parent=None, current_hotkey=None):
        """
        HotkeyDialogの初期化
        
        Parameters
        ----------
        parent : QWidget, optional
            親ウィジェット
        current_hotkey : str, optional
            現在設定されているホットキー
        """
        super().__init__(parent)
        self.setWindowTitle(AppLabels.HOTKEY_DIALOG_TITLE)
        self.setMinimumWidth(400)
        
        # スタイルシートを設定
        self.setStyleSheet(AppStyles.HOTKEY_DIALOG_STYLE)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # ホットキー入力
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        self.hotkey_input = QLineEdit()
        if current_hotkey:
            self.hotkey_input.setText(current_hotkey)
        self.hotkey_input.setPlaceholderText(AppLabels.HOTKEY_PLACEHOLDER)
        form_layout.addRow(AppLabels.HOTKEY_LABEL, self.hotkey_input)
        
        layout.addLayout(form_layout)
        
        # 情報テキスト
        info_label = QLabel(AppLabels.HOTKEY_INFO)
        info_label.setWordWrap(True)
        info_label.setStyleSheet(AppStyles.API_KEY_INFO_LABEL_STYLE)
        layout.addWidget(info_label)
        
        # ボタン
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.save_button = QPushButton(AppLabels.SAVE_BUTTON)
        self.save_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton(AppLabels.CANCEL_BUTTON)
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_hotkey(self):
        """
        入力されたホットキーを返す
        
        Returns
        -------
        str
            入力されたホットキー文字列
        """
        return self.hotkey_input.text() 