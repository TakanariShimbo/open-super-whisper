"""
システム指示管理用のダイアログモジュール

文字起こしの精度やフォーマットを向上させるためのシステム指示を追加・管理するダイアログを提供します
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QListWidget
)

from src.gui.labels import AppLabels
from src.gui.styles import AppStyles

class SystemInstructionsDialog(QDialog):
    """
    システム指示を管理するためのダイアログ
    
    文字起こしの精度やフォーマットを向上させるためのシステム指示を
    追加・管理するためのダイアログウィンドウ
    """
    
    def __init__(self, parent=None, instructions=None):
        """
        SystemInstructionsDialogの初期化
        
        Parameters
        ----------
        parent : QWidget, optional
            親ウィジェット
        instructions : list, optional
            初期表示する指示のリスト
        """
        super().__init__(parent)
        self.setWindowTitle(AppLabels.INSTRUCTIONS_DIALOG_TITLE)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # スタイルシートを設定
        self.setStyleSheet(AppStyles.SYSTEM_INSTRUCTIONS_DIALOG_STYLE)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # タイトルとガイダンス
        title_label = QLabel(AppLabels.INSTRUCTIONS_DIALOG_TITLE)
        title_label.setProperty("class", "sectionTitle")
        layout.addWidget(title_label)
        
        # 説明ラベル
        info_label = QLabel(AppLabels.INSTRUCTIONS_INFO)
        info_label.setWordWrap(True)
        info_label.setProperty("class", "info")
        layout.addWidget(info_label)
        
        # 指示リスト
        instructions_label = QLabel(AppLabels.INSTRUCTIONS_SECTION_TITLE)
        instructions_label.setProperty("class", "sectionTitle")
        layout.addWidget(instructions_label)
        
        self.instructions_list = QListWidget()
        if instructions:
            for instruction in instructions:
                self.instructions_list.addItem(instruction)
        
        layout.addWidget(self.instructions_list)
        
        # 指示追加インターフェース
        add_layout = QHBoxLayout()
        add_layout.setSpacing(8)
        
        self.instruction_input = QLineEdit()
        self.instruction_input.setPlaceholderText(AppLabels.INSTRUCTIONS_PLACEHOLDER)
        
        self.add_button = QPushButton(AppLabels.ADD_BUTTON)
        self.add_button.setFixedWidth(80)
        self.add_button.clicked.connect(self.add_instruction)
        
        add_layout.addWidget(self.instruction_input, 1)
        add_layout.addWidget(self.add_button, 0)
        layout.addLayout(add_layout)
        
        # アクションボタン
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        self.remove_button = QPushButton(AppLabels.REMOVE_SELECTED)
        self.remove_button.setProperty("class", "secondary")
        self.remove_button.clicked.connect(self.remove_instruction)
        
        self.clear_button = QPushButton(AppLabels.REMOVE_ALL)
        self.clear_button.setProperty("class", "danger")
        self.clear_button.clicked.connect(self.clear_instructions)
        
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)
        
        # ダイアログボタン
        dialog_buttons = QHBoxLayout()
        dialog_buttons.setSpacing(10)
        
        self.ok_button = QPushButton(AppLabels.OK_BUTTON)
        self.ok_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton(AppLabels.CANCEL_BUTTON)
        self.cancel_button.setProperty("class", "secondary")
        self.cancel_button.clicked.connect(self.reject)
        
        dialog_buttons.addWidget(self.cancel_button)
        dialog_buttons.addWidget(self.ok_button)
        layout.addLayout(dialog_buttons)
        
        self.setLayout(layout)
    
    def add_instruction(self):
        """
        システム指示リストに新しい指示を追加する
        """
        instruction = self.instruction_input.text().strip()
        if instruction:
            self.instructions_list.addItem(instruction)
            self.instruction_input.clear()
            self.instruction_input.setFocus()
    
    def remove_instruction(self):
        """
        選択された指示をシステム指示リストから削除する
        """
        selected_items = self.instructions_list.selectedItems()
        for item in selected_items:
            self.instructions_list.takeItem(self.instructions_list.row(item))
    
    def clear_instructions(self):
        """
        システム指示リストからすべての指示を削除する
        """
        self.instructions_list.clear()
    
    def get_instructions(self):
        """
        システム指示リストの指示を取得する
        
        Returns
        -------
        list
            すべてのシステム指示のリスト
        """
        return [self.instructions_list.item(i).text() for i in range(self.instructions_list.count())] 