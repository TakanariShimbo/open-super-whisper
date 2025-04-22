"""
シンプルな入力ダイアログモジュール

タイトルとテキスト入力フィールドを持つシンプルなダイアログを提供します
"""

import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QLabel, QApplication, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.gui.resources.labels import AppLabels
from src.gui.resources.styles import AppStyles, AppTheme

class SimpleInputDialog(QDialog):
    """
    テキスト入力のためのシンプルなダイアログ
    
    タイトルとテキスト入力フィールドを持つシンプルなダイアログ
    """
    
    def __init__(self, parent=None, title="", prompt="", initial_text=""):
        """
        SimpleInputDialogの初期化
        
        Parameters
        ----------
        parent : QWidget, optional
            親ウィジェット
        title : str, optional
            ダイアログのタイトル
        prompt : str, optional
            入力フィールドの上に表示するプロンプトテキスト
        initial_text : str, optional
            入力フィールドの初期テキスト
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        
        # スタイルシートを設定
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
        title_label = QLabel(title)
        title_label.setObjectName("dialogTitle")
        layout.addWidget(title_label)
        
        # セパレーター
        separator = QFrame()
        separator.setObjectName("separatorLine")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        # プロンプトテキスト
        prompt_label = QLabel(prompt)
        prompt_label.setWordWrap(True)
        layout.addWidget(prompt_label)
        
        # 入力フィールド
        self.text_input = QLineEdit()
        if initial_text:
            self.text_input.setText(initial_text)
        self.text_input.selectAll()  # 初期テキストを選択状態にする
        layout.addWidget(self.text_input)
        
        # ボタン
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.cancel_button = QPushButton(AppLabels.CANCEL_BUTTON)
        self.cancel_button.setProperty("class", "secondary")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setFixedWidth(100)
        
        self.ok_button = QPushButton(AppLabels.OK_BUTTON)
        self.ok_button.setProperty("class", "primary")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setFixedWidth(100)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
        main_layout.addWidget(dialog_frame)
        
        # Enter キーでOKボタンをクリックするように設定
        self.text_input.returnPressed.connect(self.ok_button.click)
        
        # 入力フィールドにフォーカスを設定
        self.text_input.setFocus()
    
    def textValue(self):
        """
        入力されたテキストを返す
        
        Returns
        -------
        str
            入力されたテキスト
        """
        return self.text_input.text()

# スタンドアロンでテスト実行時の処理
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # テスト用ダイアログの作成と表示
    dialog = SimpleInputDialog(
        title="テストダイアログ",
        prompt="テキストを入力してください:",
        initial_text="初期テキスト"
    )
    result = dialog.exec()
    
    # 結果の表示
    if result == QDialog.DialogCode.Accepted:
        print(f"入力されたテキスト: {dialog.textValue()}")
    else:
        print("キャンセルされました")
    
    sys.exit() 