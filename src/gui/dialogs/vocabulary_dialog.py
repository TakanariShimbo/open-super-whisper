"""
カスタム語彙管理用のダイアログモジュール

文字起こし精度向上のためのカスタム語彙を追加・管理するダイアログを提供します
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QListWidget
)

from src.gui.labels import AppLabels
from src.gui.styles import AppStyles

class VocabularyDialog(QDialog):
    """
    カスタム語彙管理のためのダイアログ
    
    文字起こし精度向上のためのカスタム語彙を追加・管理するダイアログウィンドウ
    """
    
    def __init__(self, parent=None, vocabulary=None):
        """
        VocabularyDialogの初期化
        
        Parameters
        ----------
        parent : QWidget, optional
            親ウィジェット
        vocabulary : list, optional
            初期表示する語彙のリスト
        """
        super().__init__(parent)
        self.setWindowTitle(AppLabels.VOCABULARY_DIALOG_TITLE)
        self.setMinimumWidth(450)
        self.setMinimumHeight(350)
        
        # スタイルシートを設定
        self.setStyleSheet(AppStyles.VOCABULARY_DIALOG_STYLE)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # タイトルラベル
        title_label = QLabel(AppLabels.VOCABULARY_SECTION_TITLE)
        title_label.setProperty("class", "sectionTitle")
        layout.addWidget(title_label)
        
        # 語彙リスト
        self.vocabulary_list = QListWidget()
        if vocabulary:
            for term in vocabulary:
                self.vocabulary_list.addItem(term)
        
        layout.addWidget(self.vocabulary_list)
        
        # 用語追加インターフェース
        add_layout = QHBoxLayout()
        add_layout.setSpacing(8)
        
        self.term_input = QLineEdit()
        self.term_input.setPlaceholderText(AppLabels.VOCABULARY_PLACEHOLDER)
        
        self.add_button = QPushButton(AppLabels.ADD_BUTTON)
        self.add_button.setFixedWidth(80)
        self.add_button.clicked.connect(self.add_term)
        
        add_layout.addWidget(self.term_input, 1)
        add_layout.addWidget(self.add_button, 0)
        layout.addLayout(add_layout)
        
        # アクションボタン
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        self.remove_button = QPushButton(AppLabels.REMOVE_SELECTED)
        self.remove_button.setProperty("class", "secondary")
        self.remove_button.clicked.connect(self.remove_term)
        
        self.clear_button = QPushButton(AppLabels.REMOVE_ALL)
        self.clear_button.setProperty("class", "danger")
        self.clear_button.clicked.connect(self.clear_terms)
        
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
    
    def add_term(self):
        """
        語彙リストに新しい単語を追加する
        """
        term = self.term_input.text().strip()
        if term:
            self.vocabulary_list.addItem(term)
            self.term_input.clear()
            self.term_input.setFocus()
    
    def remove_term(self):
        """
        選択された単語を語彙リストから削除する
        """
        selected_items = self.vocabulary_list.selectedItems()
        for item in selected_items:
            self.vocabulary_list.takeItem(self.vocabulary_list.row(item))
    
    def clear_terms(self):
        """
        語彙リストからすべての単語を削除する
        """
        self.vocabulary_list.clear()
    
    def get_vocabulary(self):
        """
        語彙リストの単語を取得する
        
        Returns
        -------
        list
            すべての語彙単語のリスト
        """
        return [self.vocabulary_list.item(i).text() for i in range(self.vocabulary_list.count())] 