"""
OpenAI APIキー設定用のダイアログモジュール

APIキーの入力、保存、表示を管理するダイアログウィンドウを提供します
"""

import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QLabel, QMessageBox, QApplication, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.gui.resources.labels import AppLabels
from src.gui.resources.styles import AppStyles, AppTheme
from src.gui.components.dialogs.simple_message_dialog import SimpleMessageDialog

class APIKeyDialog(QDialog):
    """
    OpenAI APIキーを入力するためのダイアログ
    
    APIキーの入力、保存、表示を管理するダイアログウィンドウ
    """
    
    # シグナル定義
    api_key_updated = pyqtSignal(str)
    
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
        
        # スタイルシートを設定 - 新しいスタイル適用方法
        self.setStyleSheet(AppStyles.get_dialog_style())
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(AppTheme.MAIN_MARGIN, AppTheme.MAIN_MARGIN, 
                                      AppTheme.MAIN_MARGIN, AppTheme.MAIN_MARGIN)
        main_layout.setSpacing(AppTheme.MAIN_SPACING)
        
        # ダイアログフレーム
        dialog_frame = QFrame(self)
        dialog_frame.setObjectName("dialogFrame")
        layout = QVBoxLayout(dialog_frame)
        layout.setContentsMargins(int(AppTheme.PADDING_MD.split()[0].replace("px", "")), 
                                int(AppTheme.PADDING_MD.split()[0].replace("px", "")),
                                int(AppTheme.PADDING_MD.split()[0].replace("px", "")), 
                                int(AppTheme.PADDING_MD.split()[0].replace("px", "")))
        layout.setSpacing(int(AppTheme.SPACING_MD.replace("px", "")))
        
        # ダイアログタイトル
        title_label = QLabel(AppLabels.API_KEY_DIALOG_TITLE)
        title_label.setObjectName("dialogTitle")
        layout.addWidget(title_label)
        
        # セパレーター
        separator = QFrame()
        separator.setObjectName("separatorLine")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        # APIキー入力
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        self.api_key_input = QLineEdit()
        if api_key:
            self.api_key_input.setText(api_key)
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow(QLabel(AppLabels.API_KEY_LABEL), self.api_key_input)
        
        layout.addLayout(form_layout)
        
        # 情報テキスト
        info_label = QLabel(AppLabels.API_KEY_INFO)
        info_label.setWordWrap(True)
        info_label.setStyleSheet(AppStyles.INFO_LABEL_STYLE)
        layout.addWidget(info_label)
        
        # ボタン
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.cancel_button = QPushButton(AppLabels.CANCEL_BUTTON)
        self.cancel_button.setProperty("class", "secondary")
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton(AppLabels.SAVE_BUTTON)
        self.save_button.setProperty("class", "primary")
        self.save_button.clicked.connect(self.accept_with_validation)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        main_layout.addWidget(dialog_frame)
    
    def get_api_key(self):
        """
        入力されたAPIキーを返す
        
        Returns
        -------
        str
            入力されたAPIキー
        """
        return self.api_key_input.text()

    def accept_with_validation(self):
        """
        入力内容を検証して保存
        """
        api_key = self.api_key_input.text().strip()
        
        # APIキーが空の場合は警告表示
        if not api_key:
            SimpleMessageDialog.show_message(
                self,
                AppLabels.WARNING_TITLE,
                AppLabels.APIKEY_EMPTY_WARNING,
                SimpleMessageDialog.WARNING
            )
            return
        
        # APIキーが短すぎる場合は警告表示
        if len(api_key) < 10:
            SimpleMessageDialog.show_message(
                self,
                AppLabels.WARNING_TITLE,
                AppLabels.APIKEY_TOO_SHORT_WARNING,
                SimpleMessageDialog.WARNING
            )
            return
        
        # シグナル発行
        self.api_key_updated.emit(api_key)
        
        # ダイアログを閉じる
        self.accept()

# スタンドアロンでテスト実行時の処理
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # テスト用ダイアログの作成と表示
    dialog = APIKeyDialog()
    result = dialog.exec()
    
    # 結果の表示
    if result == QDialog.DialogCode.Accepted:
        print(f"APIキーが設定されました: {dialog.api_key_input.text()}")
    else:
        print("キャンセルされました")
    
    sys.exit() 