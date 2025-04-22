"""
シンプルなメッセージダイアログモジュール

警告、確認、情報を表示するためのシンプルなダイアログを提供します
"""

import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QApplication, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap

from src.gui.resources.labels import AppLabels
from src.gui.resources.styles import AppStyles, AppTheme
from src.gui.utils.resource_helper import getResourcePath

class SimpleMessageDialog(QDialog):
    """
    メッセージを表示するためのシンプルなダイアログ
    
    警告、確認、情報表示などのためのダイアログ
    """
    
    # メッセージタイプ
    INFO = 0
    WARNING = 1
    QUESTION = 2
    
    def __init__(self, parent=None, title="", message="", message_type=INFO, buttons=None):
        """
        SimpleMessageDialogの初期化
        
        Parameters
        ----------
        parent : QWidget, optional
            親ウィジェット
        title : str, optional
            ダイアログのタイトル
        message : str, optional
            表示するメッセージ
        message_type : int, optional
            メッセージの種類（INFO, WARNING, QUESTION）
        buttons : list, optional
            表示するボタンのラベルリスト。デフォルトではOKのみ。
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        
        # 結果の初期化
        self.result_value = None
        
        # スタイルシートを設定
        self.setStyleSheet(AppStyles.get_dialog_style())
        
        # デフォルトのボタン設定
        if buttons is None:
            if message_type == self.QUESTION:
                buttons = [AppLabels.YES_BUTTON, AppLabels.NO_BUTTON]
            else:
                buttons = [AppLabels.OK_BUTTON]
        
        # レイアウト設定
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
        title_label = QLabel(title)
        title_label.setObjectName("dialogTitle")
        layout.addWidget(title_label)
        
        # セパレーター
        separator = QFrame()
        separator.setObjectName("separatorLine")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        # アイコンとメッセージのレイアウト
        message_layout = QHBoxLayout()
        message_layout.setSpacing(20)
        
        # アイコン
        icon_label = QLabel()
        icon_path = ""
        
        if message_type == self.INFO:
            icon_path = getResourcePath("assets/info.png")
        elif message_type == self.WARNING:
            icon_path = getResourcePath("assets/warning.png")
        elif message_type == self.QUESTION:
            icon_path = getResourcePath("assets/question.png")
        
        # アイコンがある場合は表示
        if icon_path and isinstance(icon_path, str) and len(icon_path) > 0:
            icon_pixmap = QPixmap(icon_path)
            if not icon_pixmap.isNull():
                icon_label.setPixmap(icon_pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio))
                message_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignTop)
        
        # メッセージテキスト
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_layout.addWidget(message_label, 1)
        
        layout.addLayout(message_layout)
        
        # ボタン
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()
        
        for i, button_text in enumerate(buttons):
            button = QPushButton(button_text)
            
            # 最初のボタンはprimary、それ以外はsecondary
            if i == 0 and message_type != self.QUESTION:
                button.setProperty("class", "primary")
            elif i == 0 and message_type == self.QUESTION:
                button.setProperty("class", "danger")  # YESボタンは危険なアクションの場合
            else:
                button.setProperty("class", "secondary")
            
            button.setFixedWidth(100)
            button.clicked.connect(lambda checked, text=button_text: self.handle_button_click(text))
            button_layout.addWidget(button)
        
        layout.addLayout(button_layout)
        
        main_layout.addWidget(dialog_frame)
    
    def handle_button_click(self, button_text):
        """ボタンクリック時の処理"""
        self.result_value = button_text
        self.accept()
    
    def get_result(self):
        """ダイアログの結果を返す"""
        return self.result_value
    
    @staticmethod
    def show_message(parent, title, message, message_type=INFO):
        """
        情報・警告メッセージを表示する
        
        Parameters
        ----------
        parent : QWidget
            親ウィジェット
        title : str
            ダイアログのタイトル
        message : str
            表示するメッセージ
        message_type : int
            メッセージの種類（INFO, WARNING）
            
        Returns
        -------
        str
            クリックされたボタンのテキスト
        """
        dialog = SimpleMessageDialog(parent, title, message, message_type)
        dialog.exec()
        return dialog.get_result()
    
    @staticmethod
    def show_confirmation(parent, title, message):
        """
        確認メッセージを表示する
        
        Parameters
        ----------
        parent : QWidget
            親ウィジェット
        title : str
            ダイアログのタイトル
        message : str
            表示するメッセージ
            
        Returns
        -------
        bool
            Yesが選択されたかどうか
        """
        dialog = SimpleMessageDialog(parent, title, message, SimpleMessageDialog.QUESTION)
        dialog.exec()
        return dialog.get_result() == AppLabels.YES_BUTTON

# スタンドアロンでテスト実行時の処理
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 警告メッセージのテスト
    warning_result = SimpleMessageDialog.show_message(
        None, 
        "警告", 
        "APIキーを入力してください。", 
        SimpleMessageDialog.WARNING
    )
    print(f"警告ダイアログの結果: {warning_result}")
    
    # 確認ダイアログのテスト
    confirm_result = SimpleMessageDialog.show_confirmation(
        None,
        "セット削除",
        "セット「テスト」を削除してもよろしいですか？"
    )
    print(f"確認ダイアログの結果: {confirm_result}")
    
    sys.exit() 