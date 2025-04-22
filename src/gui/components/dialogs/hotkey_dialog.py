"""
グローバルホットキー設定用のダイアログモジュール

録音の開始/停止に使用するグローバルホットキーを設定するためのダイアログを提供します
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QLabel, QMessageBox, QWidget, QApplication, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QKeyEvent, QKeySequence, QFont

from src.gui.resources.labels import AppLabels
from src.gui.resources.styles import AppStyles, AppTheme
from src.core.hotkeys import HotkeyManager
from src.gui.utils.resource_helper import getResourcePath

class HotkeyCapture(QWidget):
    """キーの組み合わせをキャプチャするカスタムウィジェット"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 押されたキーの組み合わせを表示するラベル
        self.display_label = QLabel("キーを押してください...")
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 新しいスタイル適用方法
        custom_input_style = f"""
            border: 1px solid {AppTheme.BORDER};
            border-radius: {AppTheme.RADIUS_SM};
            padding: 8px;
            background-color: {AppTheme.SURFACE};
            min-height: 24px;
        """
        self.display_label.setStyleSheet(custom_input_style)
        
        font = QFont()
        font.setBold(True)
        self.display_label.setFont(font)
        
        # クリアボタン
        self.clear_button = QPushButton("クリア")
        self.clear_button.clicked.connect(self.clear_hotkey)
        self.clear_button.setFixedWidth(80)
        self.clear_button.setProperty("class", "secondary")
        
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
    
    def __init__(self, parent=None, current_hotkey=""):
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
        self.setStyleSheet(AppStyles.get_dialog_style())
        self.setMinimumWidth(450)  # ダイアログ幅を広げる
        
        self.current_hotkey = current_hotkey
        
        # UI初期化
        self.init_ui()
        
    def init_ui(self):
        """UIの初期化"""
        # メインレイアウト
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
        title_label = QLabel(AppLabels.HOTKEY_DIALOG_TITLE)
        title_label.setObjectName("dialogTitle")
        layout.addWidget(title_label)
        
        # セパレーター
        separator = QFrame()
        separator.setObjectName("separatorLine")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        # ホットキーキャプチャーウィジェット
        self.hotkey_capture = HotkeyCapture()
        if self.current_hotkey:
            self.hotkey_capture.set_hotkey(self.current_hotkey)
        
        # 説明テキスト
        info_label = QLabel(AppLabels.HOTKEY_INFO)
        info_label.setStyleSheet(AppStyles.INFO_LABEL_STYLE)
        info_label.setWordWrap(True)
        
        # ウィジェットを配置
        layout.addWidget(QLabel(AppLabels.HOTKEY_LABEL))
        layout.addWidget(self.hotkey_capture)
        layout.addWidget(info_label)
        
        # ボタンレイアウト
        button_layout = QHBoxLayout()
        
        # キャンセルボタン
        self.cancel_button = QPushButton(AppLabels.CANCEL_BUTTON)
        self.cancel_button.setProperty("class", "secondary")
        self.cancel_button.clicked.connect(self.reject)
        
        # 保存ボタン
        self.save_button = QPushButton(AppLabels.SAVE_BUTTON)
        self.save_button.setProperty("class", "primary")
        self.save_button.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        main_layout.addWidget(dialog_frame)
    
    def get_hotkey(self):
        """設定されたホットキーを取得"""
        return self.hotkey_capture.get_hotkey()
    
    def clear_hotkey(self):
        """ホットキーをクリア"""
        self.hotkey_capture.clear_hotkey()

# スタンドアロンでテスト実行時の処理
if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    # テスト用ダイアログを表示
    dialog = HotkeyDialog(current_hotkey="ctrl+shift+r")
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        print(f"設定されたホットキー: {dialog.get_hotkey()}")
    else:
        print("キャンセルされました")
        
    sys.exit() 