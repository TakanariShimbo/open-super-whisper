"""
OpenAI APIキー設定用のダイアログモジュール

APIキーの入力、保存、表示を管理するダイアログウィンドウを提供します
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QLabel
)

from src.gui.labels import AppLabels
from src.gui.styles import AppStyles

class APIKeyDialog(QDialog):
    """
    OpenAI APIキーを入力するためのダイアログ
    
    APIキーの入力、保存、表示を管理するダイアログウィンドウ
    """
    
    def __init__(self, parent=None, api_key=None):
        """
        APIKeyDialogの初期化
        
        Parameters
        ----------
        parent : QWidget, optional
            親ウィジェット
        api_key : str, optional
            初期表示するAPIキー
        """
        super().__init__(parent)
        self.setWindowTitle(AppLabels.API_KEY_DIALOG_TITLE)
        self.setMinimumWidth(400)
        
        # スタイルシートを設定
        self.setStyleSheet(AppStyles.API_KEY_DIALOG_STYLE)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # APIキー入力
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        self.api_key_input = QLineEdit()
        if api_key:
            self.api_key_input.setText(api_key)
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow(AppLabels.API_KEY_LABEL, self.api_key_input)
        
        layout.addLayout(form_layout)
        
        # 情報テキスト
        info_label = QLabel(AppLabels.API_KEY_INFO)
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
    
    def get_api_key(self):
        """
        入力されたAPIキーを返す
        
        Returns
        -------
        str
            入力されたAPIキー
        """
        return self.api_key_input.text() 