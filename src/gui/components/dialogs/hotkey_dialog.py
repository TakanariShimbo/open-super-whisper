"""
グローバルホットキー設定用のダイアログモジュール

録音の開始/停止に使用するグローバルホットキーを設定するためのダイアログを提供します
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QLabel, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QKeySequence, QFont

from src.gui.resources.labels import AppLabels
from src.gui.resources.styles import AppStyles
from src.core.hotkeys import HotkeyManager

class HotkeyCapture(QWidget):
    """キーの組み合わせをキャプチャするカスタムウィジェット"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 押されたキーの組み合わせを表示するラベル
        self.display_label = QLabel("キーを押してください...")
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_label.setStyleSheet("""
            border: 1px solid #E2E6EC;
            border-radius: 4px;
            padding: 8px;
            background-color: white;
            min-height: 24px;
        """)
        font = QFont()
        font.setBold(True)
        self.display_label.setFont(font)
        
        # クリアボタン
        self.clear_button = QPushButton("クリア")
        self.clear_button.clicked.connect(self.clear_hotkey)
        self.clear_button.setFixedWidth(80)
        
        # 水平レイアウトでラベルとクリアボタンを配置
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.display_label)
        h_layout.addWidget(self.clear_button)
        
        self.layout.addLayout(h_layout)
        
        # 現在の修飾キーとキーの状態
        self.current_modifiers = []
        self.current_key = None
        self.hotkey_text = ""
        
        # ウィジェットがフォーカスを受け取れるようにする
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def keyPressEvent(self, event: QKeyEvent):
        """キーが押されたときのイベントハンドラ"""
        key = event.key()
        modifiers = event.modifiers()
        
        # 修飾キーのマッピング
        modifier_map = {
            Qt.KeyboardModifier.ControlModifier: "ctrl",
            Qt.KeyboardModifier.AltModifier: "alt",
            Qt.KeyboardModifier.ShiftModifier: "shift",
            Qt.KeyboardModifier.MetaModifier: "cmd"  # Windows/Linuxでは通常Win, MacOSではCommand
        }
        
        # 修飾キー以外のキーの処理（Escapeキーは無視する）
        if key != Qt.Key.Key_Escape:
            # 修飾キーの検出
            self.current_modifiers = []
            for mod, name in modifier_map.items():
                if modifiers & mod:
                    self.current_modifiers.append(name)
            
            # 特殊キーの名前マッピング
            key_name = ""
            if key in [Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_Shift, Qt.Key.Key_Meta]:
                # 修飾キーだけの場合は何もしない（他のキーと組み合わせる必要がある）
                pass
            else:
                # キー名を取得
                key_name = QKeySequence(key).toString()
            
            # 修飾キーが存在し、かつ通常キーがある場合のみ設定
            if key_name and (self.current_modifiers or key_name.lower() not in ["ctrl", "alt", "shift", "meta"]):
                self.current_key = key_name
                
                # ホットキーの文字列を作成
                parts = self.current_modifiers.copy()
                if self.current_key:
                    parts.append(self.current_key.lower())
                
                self.hotkey_text = "+".join(parts)
                self.display_label.setText(self.hotkey_text)
        
        event.accept()
    
    def clear_hotkey(self):
        """ホットキー設定をクリアする"""
        self.current_modifiers = []
        self.current_key = None
        self.hotkey_text = ""
        self.display_label.setText("キーを押してください...")
    
    def get_hotkey(self):
        """現在設定されているホットキーを返す"""
        return self.hotkey_text
    
    def set_hotkey(self, hotkey):
        """ホットキーを設定する"""
        if hotkey:
            self.hotkey_text = hotkey
            self.display_label.setText(self.hotkey_text)
        else:
            self.clear_hotkey()

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
        
        # ホットキーマネージャーのインスタンス（検証用）
        self.hotkey_manager = HotkeyManager()
        
        # スタイルシートを設定
        self.setStyleSheet(AppStyles.HOTKEY_DIALOG_STYLE)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # ホットキー入力
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # カスタムのホットキーキャプチャウィジェットを使用
        self.hotkey_capture = HotkeyCapture()
        if current_hotkey:
            self.hotkey_capture.set_hotkey(current_hotkey)
        
        form_layout.addRow(AppLabels.HOTKEY_LABEL, self.hotkey_capture)
        layout.addLayout(form_layout)
        
        # 情報テキスト
        info_label = QLabel(AppLabels.HOTKEY_INFO)
        info_label.setWordWrap(True)
        info_label.setStyleSheet(AppStyles.API_KEY_INFO_LABEL_STYLE)
        layout.addWidget(info_label)
        
        # 使用方法テキスト
        usage_label = QLabel("使用方法: 設定したいキーの組み合わせを押してください。")
        usage_label.setWordWrap(True)
        usage_label.setStyleSheet(AppStyles.API_KEY_INFO_LABEL_STYLE)
        layout.addWidget(usage_label)
        
        # ボタン
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.save_button = QPushButton(AppLabels.SAVE_BUTTON)
        self.save_button.clicked.connect(self.validate_and_accept)
        
        self.cancel_button = QPushButton(AppLabels.CANCEL_BUTTON)
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def validate_and_accept(self):
        """
        ホットキー入力を検証してから受け入れる
        """
        hotkey = self.hotkey_capture.get_hotkey()
        
        if not hotkey:
            QMessageBox.warning(self, "入力エラー", "ホットキーを設定してください。")
            return
        
        # ホットキーの有効性をチェック
        if not self.hotkey_manager.is_valid_hotkey(hotkey):
            QMessageBox.warning(self, "入力エラー", "無効なホットキー形式です。")
            return
            
        # 修飾キーの存在を確認
        if not self.hotkey_manager.contains_modifier(hotkey):
            response = QMessageBox.question(
                self,
                "修飾キーがありません",
                "修飾キー（Ctrl, Alt, Shiftなど）を含まないホットキーは他のアプリケーションと衝突する可能性があります。\n\n続行しますか？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if response == QMessageBox.StandardButton.No:
                return
        
        self.accept()
    
    def get_hotkey(self):
        """
        入力されたホットキーを返す
        
        Returns
        -------
        str
            入力されたホットキー文字列
        """
        return self.hotkey_capture.get_hotkey() 