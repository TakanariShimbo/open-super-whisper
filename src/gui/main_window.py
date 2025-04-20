import os
import sys
import threading
import time
from pathlib import Path
from datetime import datetime
import winreg
import ctypes
import shutil

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QComboBox, QFileDialog,
    QCheckBox, QLineEdit, QListWidget, QMessageBox, QSplitter,
    QStatusBar, QToolBar, QDialog, QGridLayout, QFormLayout,
    QSystemTrayIcon, QMenu, QStyle, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSettings, QUrl
from PyQt6.QtGui import QIcon, QAction, QFont
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import keyboard

from src.core.audio_recorder import AudioRecorder
from src.core.whisper_api import WhisperTranscriber

# define hotkey settings
DEFAULT_HOTKEY = "ctrl+shift+r"

# PyInstallerでパス解決を行うヘルパー関数
def getResourcePath(relative_path):
    """PyInstallerでバンドルされている場合や通常実行時のリソースパスを解決します"""
    try:
        # PyInstallerでバンドルされている場合
        base_path = getattr(sys, '_MEIPASS', None)
        if base_path:
            return os.path.join(base_path, relative_path)
        
        # 通常実行の場合
        if getattr(sys, 'frozen', False):
            # 実行可能ファイルとして実行している場合
            base_path = os.path.dirname(sys.executable)
        else:
            # スクリプトとして実行している場合
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        return os.path.join(base_path, relative_path)
    except Exception as e:
        print(f"リソースパス解決エラー: {e}")
        return relative_path

class APIKeyDialog(QDialog):
    """Dialog to enter OpenAI API key"""
    
    def __init__(self, parent=None, api_key=None):
        super().__init__(parent)
        self.setWindowTitle("OpenAI APIキー")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # API key input
        form_layout = QFormLayout()
        self.api_key_input = QLineEdit()
        if api_key:
            self.api_key_input.setText(api_key)
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("APIキー:", self.api_key_input)
        
        layout.addLayout(form_layout)
        
        # Information text
        info_label = QLabel(
            "このアプリケーションを使用するにはOpenAI APIキーが必要です。"
            "お持ちでない場合は、https://platform.openai.com/api-keys から取得できます。"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("キャンセル")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_api_key(self):
        """Return the entered API key"""
        return self.api_key_input.text()


class VocabularyDialog(QDialog):
    """Dialog to manage custom vocabulary"""
    
    def __init__(self, parent=None, vocabulary=None):
        super().__init__(parent)
        self.setWindowTitle("カスタム語彙")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        layout = QVBoxLayout()
        
        # Vocabulary list
        self.vocabulary_list = QListWidget()
        if vocabulary:
            for term in vocabulary:
                self.vocabulary_list.addItem(term)
        
        layout.addWidget(QLabel("カスタム語彙の単語:"))
        layout.addWidget(self.vocabulary_list)
        
        # Add term interface
        add_layout = QHBoxLayout()
        self.term_input = QLineEdit()
        self.term_input.setPlaceholderText("新しい単語を入力...")
        self.add_button = QPushButton("追加")
        self.add_button.clicked.connect(self.add_term)
        
        add_layout.addWidget(self.term_input)
        add_layout.addWidget(self.add_button)
        layout.addLayout(add_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.remove_button = QPushButton("選択項目を削除")
        self.remove_button.clicked.connect(self.remove_term)
        self.clear_button = QPushButton("すべて削除")
        self.clear_button.clicked.connect(self.clear_terms)
        
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)
        
        # Dialog buttons
        dialog_buttons = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("キャンセル")
        self.cancel_button.clicked.connect(self.reject)
        
        dialog_buttons.addWidget(self.cancel_button)
        dialog_buttons.addWidget(self.ok_button)
        layout.addLayout(dialog_buttons)
        
        self.setLayout(layout)
    
    def add_term(self):
        """Add a new term to the vocabulary list"""
        term = self.term_input.text().strip()
        if term:
            self.vocabulary_list.addItem(term)
            self.term_input.clear()
    
    def remove_term(self):
        """Remove the selected term from the vocabulary list"""
        selected_items = self.vocabulary_list.selectedItems()
        for item in selected_items:
            self.vocabulary_list.takeItem(self.vocabulary_list.row(item))
    
    def clear_terms(self):
        """Clear all terms from the vocabulary list"""
        self.vocabulary_list.clear()
    
    def get_vocabulary(self):
        """Return the list of vocabulary terms"""
        return [self.vocabulary_list.item(i).text() for i in range(self.vocabulary_list.count())]


class SystemInstructionsDialog(QDialog):
    """システム指示を管理するダイアログ"""
    
    def __init__(self, parent=None, instructions=None):
        super().__init__(parent)
        self.setWindowTitle("システム指示")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # 説明ラベル
        info_label = QLabel(
            "ここで文字起こしのための特別な指示を設定できます。例：\n"
            "- \"えー、あの、などのフィラーを無視してください\"\n"
            "- \"句読点を適切に入れてください\"\n"
            "- \"段落に分けてください\""
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 指示リスト
        self.instructions_list = QListWidget()
        if instructions:
            for instruction in instructions:
                self.instructions_list.addItem(instruction)
        
        layout.addWidget(QLabel("システム指示:"))
        layout.addWidget(self.instructions_list)
        
        # 指示追加インターフェース
        add_layout = QHBoxLayout()
        self.instruction_input = QLineEdit()
        self.instruction_input.setPlaceholderText("新しい指示を入力...")
        self.add_button = QPushButton("追加")
        self.add_button.clicked.connect(self.add_instruction)
        
        add_layout.addWidget(self.instruction_input)
        add_layout.addWidget(self.add_button)
        layout.addLayout(add_layout)
        
        # アクションボタン
        button_layout = QHBoxLayout()
        self.remove_button = QPushButton("選択項目を削除")
        self.remove_button.clicked.connect(self.remove_instruction)
        self.clear_button = QPushButton("すべて削除")
        self.clear_button.clicked.connect(self.clear_instructions)
        
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)
        
        # ダイアログボタン
        dialog_buttons = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("キャンセル")
        self.cancel_button.clicked.connect(self.reject)
        
        dialog_buttons.addWidget(self.cancel_button)
        dialog_buttons.addWidget(self.ok_button)
        layout.addLayout(dialog_buttons)
        
        self.setLayout(layout)
    
    def add_instruction(self):
        """新しい指示を追加"""
        instruction = self.instruction_input.text().strip()
        if instruction:
            self.instructions_list.addItem(instruction)
            self.instruction_input.clear()
    
    def remove_instruction(self):
        """選択された指示を削除"""
        selected_items = self.instructions_list.selectedItems()
        for item in selected_items:
            self.instructions_list.takeItem(self.instructions_list.row(item))
    
    def clear_instructions(self):
        """全ての指示を削除"""
        self.instructions_list.clear()
    
    def get_instructions(self):
        """指示リストを返す"""
        return [self.instructions_list.item(i).text() for i in range(self.instructions_list.count())]


class StatusIndicatorWindow(QWidget):
    """状態を示す小さなウィンドウ（録音中/文字起こし中/コピー完了）"""
    
    # 状態の定義
    MODE_RECORDING = 0
    MODE_TRANSCRIBING = 1
    MODE_COPIED = 2
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # ウィンドウ設定
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(150, 90)
        
        # レイアウト設定
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # 本体部分のレイアウト
        self.frame = QFrame()
        self.frame.setObjectName("statusFrame")
        
        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(4)
        
        # 状態テキスト
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)
        
        # 録音時間表示ラベル
        self.timer_label = QLabel()
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setObjectName("timerLabel")
        layout.addWidget(self.timer_label)
        
        main_layout.addWidget(self.frame)
        
        # コピー完了時の自動非表示タイマー
        self.auto_hide_timer = QTimer(self)
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.hide)
        
        # スタイルシート設定
        self.setStyleSheet("""
            #statusFrame {
                border-radius: 12px;
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 rgba(60, 60, 60, 220), 
                                         stop:1 rgba(40, 40, 40, 220));
                border: 1px solid rgba(255, 255, 255, 40);
            }
            
            #statusLabel {
                color: white;
                font-weight: bold;
                font-size: 15px;
                font-family: "Segoe UI", Arial, sans-serif;
                margin-top: 2px;
                padding: 2px;
            }
            
            #timerLabel {
                color: white;
                font-size: 20px;
                font-family: "Segoe UI", Arial, sans-serif;
                font-weight: 500;
                padding: 2px;
            }
        """)
        
        # 初期状態では非表示に設定
        self.hide()
        
        # 現在のモードを記録する変数
        self.current_mode = None
        
        # ウィンドウの位置を設定
        self.position_window()
        
        # マウスドラッグ用の変数
        self.drag_position = None
        
    def set_mode(self, mode):
        """表示モードを設定する"""
        self.current_mode = mode
        
        if mode == self.MODE_RECORDING:
            self.status_label.setText("録音中")
            self.setFixedSize(150, 90)
            self.timer_label.setText("00:00")
            self.timer_label.show()
            
            # 録音中のスタイル - 赤系のグラデーション
            self.frame.setStyleSheet("""
                #statusFrame {
                    border-radius: 12px;
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                             stop:0 rgba(220, 60, 60, 220), 
                                             stop:1 rgba(180, 40, 40, 220));
                    border: 1px solid rgba(255, 100, 100, 80);
                    box-shadow: 0px 3px 5px rgba(0, 0, 0, 40%);
                }
            """)
        
        elif mode == self.MODE_TRANSCRIBING:
            self.status_label.setText("文字起こし中")
            self.setFixedSize(150, 70)
            self.timer_label.setText("")
            self.timer_label.hide()
            
            # 文字起こし中のスタイル - 青系のグラデーション
            self.frame.setStyleSheet("""
                #statusFrame {
                    border-radius: 12px;
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                             stop:0 rgba(60, 120, 220, 220), 
                                             stop:1 rgba(40, 80, 180, 220));
                    border: 1px solid rgba(100, 150, 255, 80);
                    box-shadow: 0px 3px 5px rgba(0, 0, 0, 40%);
                }
            """)
        
        elif mode == self.MODE_COPIED:
            self.status_label.setText("コピー完了")
            self.setFixedSize(150, 70)
            self.timer_label.setText("")
            self.timer_label.hide()
            
            # コピー完了のスタイル - 緑系のグラデーション
            self.frame.setStyleSheet("""
                #statusFrame {
                    border-radius: 12px;
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                             stop:0 rgba(60, 180, 60, 220), 
                                             stop:1 rgba(40, 150, 40, 220));
                    border: 1px solid rgba(100, 220, 100, 80);
                    box-shadow: 0px 3px 5px rgba(0, 0, 0, 40%);
                }
            """)
            
            # 3秒後に非表示
            self.auto_hide_timer.start(3000)
    
    def position_window(self):
        """ウィンドウを画面の右下に配置"""
        screen_geometry = QApplication.primaryScreen().geometry()
        window_geometry = self.geometry()
        
        # 画面の右下から少し内側に配置
        x = screen_geometry.width() - window_geometry.width() - 20
        y = screen_geometry.height() - window_geometry.height() - 100
        
        self.move(x, y)
    
    def update_timer(self, time_str):
        """タイマー表示を更新（録音モード時）"""
        if self.current_mode == self.MODE_RECORDING:
            self.timer_label.setText(time_str)
        
    def mousePressEvent(self, event):
        """ウィンドウのドラッグを可能にする"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """ウィンドウを移動"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


class HotkeyDialog(QDialog):
    """Dialog to set global hotkey"""
    
    def __init__(self, parent=None, current_hotkey=None):
        super().__init__(parent)
        self.setWindowTitle("グローバルホットキー設定")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Hotkey input
        form_layout = QFormLayout()
        self.hotkey_input = QLineEdit()
        if current_hotkey:
            self.hotkey_input.setText(current_hotkey)
        self.hotkey_input.setPlaceholderText("例: ctrl+shift+r")
        form_layout.addRow("ホットキー:", self.hotkey_input)
        
        layout.addLayout(form_layout)
        
        # Information text
        info_label = QLabel(
            "録音を開始/停止するグローバルホットキーを設定します。"
            "例: ctrl+shift+r, alt+w など"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("キャンセル")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_hotkey(self):
        """Return the entered hotkey"""
        return self.hotkey_input.text()


class MainWindow(QMainWindow):
    """Main application window"""
    
    # Define custom signals
    transcription_complete = pyqtSignal(str)
    recording_status_changed = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        
        # Load settings
        self.settings = QSettings("OpenSuperWhisper", "WhisperTranscriber")
        self.api_key = self.settings.value("api_key", "")
        
        # ホットキーとクリップボード設定
        self.hotkey = self.settings.value("hotkey", DEFAULT_HOTKEY)
        self.auto_copy = self.settings.value("auto_copy", True, type=bool)
        
        # サウンド設定
        self.enable_sound = self.settings.value("enable_sound", True, type=bool)
        
        # インジケータ表示設定（デフォルトON）
        self.show_indicator = self.settings.value("show_indicator", True, type=bool)
        
        # サウンドプレーヤーの初期化
        self.setup_sound_players()
        
        # Initialize components
        self.audio_recorder = AudioRecorder()
        
        # 状態表示ウィンドウ
        self.status_indicator_window = StatusIndicatorWindow()
        # 初期モードを録音中に設定
        self.status_indicator_window.set_mode(StatusIndicatorWindow.MODE_RECORDING)
        # 初期状態では表示しない - 録音開始時に表示する
        
        try:
            self.whisper_transcriber = WhisperTranscriber(api_key=self.api_key)
        except ValueError:
            self.whisper_transcriber = None
        
        # Setup UI
        self.init_ui()
        
        # Connect signals
        self.transcription_complete.connect(self.on_transcription_complete)
        self.recording_status_changed.connect(self.update_recording_status)
        
        # Check API key
        if not self.api_key:
            self.show_api_key_dialog()
            
        # Setup additional connections
        self.setup_connections()
        
        # Setup global hotkey
        self.setup_global_hotkey()
        
        # Setup system tray
        self.setup_system_tray()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Open Super Whisper")
        self.setMinimumSize(800, 600)
        
        # アプリケーションアイコンを設定
        icon_path = getResourcePath("assets/icon.ico")
        
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # アイコンファイルが見つからない場合は標準アイコンを使用
            self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            print(f"警告: アイコンファイルが見つかりません: {icon_path}")
            
        # アプリ全体のスタイルを設定
        self.setStyleSheet("""
            * {
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 13px;
            }
            
            QMainWindow {
                background-color: #F5F5F7;
            }
            
            QToolBar {
                background-color: #F0F0F2;
                border-bottom: 1px solid #DDDDDF;
                spacing: 5px;
                padding: 5px;
                font-size: 13px;
            }
            
            QToolBar QAction {
                padding: 4px 8px;
            }
            
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }
            
            QPushButton:hover {
                background-color: #2563EB;
            }
            
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
            
            QTextEdit {
                border: 1px solid #DDDDDF;
                border-radius: 4px;
                background-color: white;
                padding: 8px;
                font-size: 14px;
            }
            
            QComboBox {
                border: 1px solid #DDDDDF;
                border-radius: 4px;
                padding: 6px 12px;
                background-color: white;
                min-width: 150px;
            }
            
            QComboBox:hover {
                border-color: #BBBBBB;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 20px;
                border-left: none;
            }
            
            QStatusBar {
                background-color: #F0F0F2;
                color: #555555;
                border-top: 1px solid #DDDDDF;
                font-size: 13px;
            }
            
            QLabel {
                color: #333333;
                font-size: 13px;
            }
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Create toolbar
        self.create_toolbar()
        
        # Control panel
        control_panel = QWidget()
        control_panel.setObjectName("controlPanel")
        control_panel.setStyleSheet("""
            #controlPanel {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #DDDDDF;
            }
        """)
        control_layout = QGridLayout()
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(12)
        
        # Recording controls
        self.record_button = QPushButton("録音開始")
        self.record_button.setObjectName("recordButton")
        self.record_button.setMinimumHeight(40)
        self.record_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.record_button.setStyleSheet("""
            #recordButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            
            #recordButton:hover {
                background-color: #2563EB;
            }
            
            #recordButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        self.record_button.clicked.connect(self.toggle_recording)
        
        # コントロールフォーム
        control_form = QWidget()
        form_layout = QFormLayout(control_form)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(10)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Language selection
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("languageCombo")
        
        # Add language options
        self.language_combo.addItem("自動検出", "")
        self.language_combo.addItem("英語", "en")
        self.language_combo.addItem("スペイン語", "es")
        self.language_combo.addItem("フランス語", "fr")
        self.language_combo.addItem("ドイツ語", "de")
        self.language_combo.addItem("イタリア語", "it")
        self.language_combo.addItem("ポルトガル語", "pt")
        self.language_combo.addItem("日本語", "ja")
        self.language_combo.addItem("韓国語", "ko")
        self.language_combo.addItem("中国語", "zh")
        self.language_combo.addItem("ロシア語", "ru")
        
        # モデル選択
        self.model_combo = QComboBox()
        self.model_combo.setObjectName("modelCombo")
        
        # モデルリストを取得してコンボボックスに追加
        for model in WhisperTranscriber.get_available_models():
            self.model_combo.addItem(model["name"], model["id"])
            # ツールチップを追加
            self.model_combo.setItemData(
                self.model_combo.count() - 1, 
                model["description"], 
                Qt.ItemDataRole.ToolTipRole
            )
        
        # 前回選択したモデルを設定
        last_model = self.settings.value("model", "whisper-1")
        index = self.model_combo.findData(last_model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
            
        # フォームにフィールドを追加
        language_label = QLabel("言語:")
        language_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        model_label = QLabel("モデル:")
        model_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        form_layout.addRow(language_label, self.language_combo)
        form_layout.addRow(model_label, self.model_combo)
        
        # レイアウトに追加
        control_layout.addWidget(self.record_button, 0, 0, 2, 1)
        control_layout.addWidget(control_form, 0, 1, 2, 5)
        control_layout.setColumnStretch(0, 1)  # 録音ボタンの列
        control_layout.setColumnStretch(1, 3)  # フォームの列
        
        control_panel.setLayout(control_layout)
        main_layout.addWidget(control_panel)
        
        # Transcription panel
        transcription_panel = QWidget()
        transcription_panel.setObjectName("transcriptionPanel")
        transcription_panel.setStyleSheet("""
            #transcriptionPanel {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #DDDDDF;
            }
        """)
        
        transcription_layout = QVBoxLayout(transcription_panel)
        transcription_layout.setContentsMargins(15, 15, 15, 15)
        
        # タイトルラベル
        title_label = QLabel("文字起こし結果")
        title_label.setObjectName("sectionTitle")
        title_label.setStyleSheet("""
            #sectionTitle {
                font-weight: bold;
                font-size: 15px;
                color: #333333;
                padding-bottom: 8px;
            }
        """)
        transcription_layout.addWidget(title_label)
        
        # Transcription output
        self.transcription_text = QTextEdit()
        self.transcription_text.setPlaceholderText("ここに文字起こしが表示されます...")
        self.transcription_text.setReadOnly(False)  # Allow editing for corrections
        self.transcription_text.setMinimumHeight(250)
        self.transcription_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                background-color: #FAFAFA;
                padding: 12px;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        
        transcription_layout.addWidget(self.transcription_text)
        main_layout.addWidget(transcription_panel, 1)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("準備完了")
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #F0F0F2;
                color: #555555;
                border-top: 1px solid #DDDDDF;
                padding: 5px;
            }
            
            QStatusBar QLabel {
                padding: 0px 5px;
            }
        """)
        
        # Recording indicator
        self.recording_indicator = QLabel("●")
        self.recording_indicator.setObjectName("recordingIndicator")
        self.recording_indicator.setStyleSheet("color: gray; font-size: 16px;")
        
        self.recording_timer_label = QLabel("00:00")
        self.recording_timer_label.setObjectName("recordingTimerLabel")
        self.recording_timer_label.setStyleSheet("color: #444; font-family: 'Roboto Mono', monospace; font-weight: bold;")
        
        self.status_bar.addPermanentWidget(self.recording_indicator)
        self.status_bar.addPermanentWidget(self.recording_timer_label)
        
        # Set up recording timer
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.update_recording_time)
        self.recording_start_time = 0
        
        # Complete the layout
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def create_toolbar(self):
        """Create the toolbar with actions"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # API Key action
        api_key_action = QAction("APIキー設定", self)
        api_key_action.triggered.connect(self.show_api_key_dialog)
        toolbar.addAction(api_key_action)
        
        # Custom vocabulary action
        vocabulary_action = QAction("カスタム語彙", self)
        vocabulary_action.triggered.connect(self.show_vocabulary_dialog)
        toolbar.addAction(vocabulary_action)
        
        # システム指示アクション
        system_instructions_action = QAction("システム指示", self)
        system_instructions_action.triggered.connect(self.show_system_instructions_dialog)
        toolbar.addAction(system_instructions_action)
        
        # Copy to clipboard action
        copy_action = QAction("クリップボードにコピー", self)
        copy_action.triggered.connect(self.copy_to_clipboard)
        toolbar.addAction(copy_action)
        
        # Add separator
        toolbar.addSeparator()
        
        # Global hotkey setting
        hotkey_action = QAction("ホットキー設定", self)
        hotkey_action.triggered.connect(self.show_hotkey_dialog)
        toolbar.addAction(hotkey_action)
        
        # Auto-copy option
        self.auto_copy_action = QAction("自動コピー", self)
        self.auto_copy_action.setCheckable(True)
        self.auto_copy_action.setChecked(self.auto_copy)
        self.auto_copy_action.triggered.connect(self.toggle_auto_copy)
        toolbar.addAction(self.auto_copy_action)
        
        # Sound option
        self.sound_action = QAction("通知音", self)
        self.sound_action.setCheckable(True)
        self.sound_action.setChecked(self.enable_sound)
        self.sound_action.triggered.connect(self.toggle_sound_option)
        toolbar.addAction(self.sound_action)
        
        # インジケータ表示オプション
        self.indicator_action = QAction("状態インジケータ", self)
        self.indicator_action.setCheckable(True)
        self.indicator_action.setChecked(self.show_indicator)
        self.indicator_action.triggered.connect(self.toggle_indicator_option)
        toolbar.addAction(self.indicator_action)
        
        # Add separator
        toolbar.addSeparator()
        
        # Exit action
        exit_action = QAction("アプリケーション終了", self)
        exit_action.triggered.connect(self.quit_application)
        exit_action.setShortcut("Alt+F4")  # 終了ショートカットを追加
        toolbar.addAction(exit_action)
    
    def show_api_key_dialog(self):
        """Show dialog to enter OpenAI API key"""
        dialog = APIKeyDialog(self, self.api_key)
        if dialog.exec():
            self.api_key = dialog.get_api_key()
            self.settings.setValue("api_key", self.api_key)
            
            # Reinitialize the transcriber with the new API key
            try:
                self.whisper_transcriber = WhisperTranscriber(api_key=self.api_key)
                self.status_bar.showMessage("APIキーが保存されました", 3000)
            except ValueError as e:
                self.whisper_transcriber = None
                QMessageBox.warning(self, "APIキーエラー", str(e))
    
    def show_vocabulary_dialog(self):
        """Show dialog to manage custom vocabulary"""
        if not self.whisper_transcriber:
            QMessageBox.warning(self, "エラー", "先にAPIキーを設定してください")
            return
            
        vocabulary = self.whisper_transcriber.get_custom_vocabulary()
        dialog = VocabularyDialog(self, vocabulary)
        
        if dialog.exec():
            new_vocabulary = dialog.get_vocabulary()
            self.whisper_transcriber.clear_custom_vocabulary()
            self.whisper_transcriber.add_custom_vocabulary(new_vocabulary)
            self.status_bar.showMessage(f"{len(new_vocabulary)}個の語彙を追加しました", 3000)
    
    def show_system_instructions_dialog(self):
        """システム指示を管理するダイアログを表示"""
        if not self.whisper_transcriber:
            QMessageBox.warning(self, "エラー", "先にAPIキーを設定してください")
            return
            
        instructions = self.whisper_transcriber.get_system_instructions()
        dialog = SystemInstructionsDialog(self, instructions)
        
        if dialog.exec():
            new_instructions = dialog.get_instructions()
            self.whisper_transcriber.clear_system_instructions()
            self.whisper_transcriber.add_system_instruction(new_instructions)
            self.status_bar.showMessage(f"{len(new_instructions)}個のシステム指示を設定しました", 3000)
    
    def toggle_recording(self):
        """Start or stop recording"""
        # GUIスレッドでの実行を保証するためQTimer.singleShotを使用
        QTimer.singleShot(0, self._toggle_recording_impl)
    
    def _toggle_recording_impl(self):
        """実際の録音切り替え処理の実装"""
        if self.audio_recorder.is_recording():
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """Start recording audio"""
        if not self.whisper_transcriber:
            QMessageBox.warning(self, "エラー", "先にAPIキーを設定してください")
            return
            
        self.record_button.setText("録音停止")
        self.audio_recorder.start_recording()
        self.recording_status_changed.emit(True)
        
        # Start recording timer
        self.recording_start_time = time.time()
        self.recording_timer.start(1000)  # Update every second
        
        # 録音中状態の表示
        if self.show_indicator:
            # 念のため、一度ウィンドウを隠してリセット
            self.status_indicator_window.hide()
            self.status_indicator_window.set_mode(StatusIndicatorWindow.MODE_RECORDING)
            self.status_indicator_window.show()
        
        self.status_bar.showMessage("録音中...")
        
        # Play start sound
        self.play_start_sound()
    
    def stop_recording(self):
        """Stop recording and start transcription"""
        self.record_button.setText("録音開始")
        audio_file = self.audio_recorder.stop_recording()
        self.recording_status_changed.emit(False)
        
        # Stop recording timer
        self.recording_timer.stop()
        
        if audio_file:
            self.status_bar.showMessage("文字起こし中...")
            self.start_transcription(audio_file)
        else:
            # 録音ファイルが作成されなかった場合は状態表示を非表示
            self.status_indicator_window.hide()
        
        # Play stop sound
        self.play_stop_sound()
    
    def update_recording_status(self, is_recording):
        """Update the recording indicator"""
        if is_recording:
            self.recording_indicator.setStyleSheet("""
                color: #E53E3E;
                font-size: 18px;
                font-weight: bold;
                animation: pulse 1.5s infinite;
                
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.6; }
                    100% { opacity: 1; }
                }
            """)
            
            # 録音ボタンのスタイルも変更
            self.record_button.setStyleSheet("""
                #recordButton {
                    background-color: #E53E3E;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 20px;
                    font-weight: bold;
                    font-size: 14px;
                }
                
                #recordButton:hover {
                    background-color: #C53030;
                }
                
                #recordButton:pressed {
                    background-color: #9B2C2C;
                }
            """)
        else:
            self.recording_indicator.setStyleSheet("color: gray; font-size: 16px;")
            
            # 録音ボタンのスタイルを元に戻す
            self.record_button.setStyleSheet("""
                #recordButton {
                    background-color: #3B82F6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 20px;
                    font-weight: bold;
                    font-size: 14px;
                }
                
                #recordButton:hover {
                    background-color: #2563EB;
                }
                
                #recordButton:pressed {
                    background-color: #1D4ED8;
                }
            """)
    
    def update_recording_time(self):
        """Update the recording time display"""
        if self.audio_recorder.is_recording():
            elapsed = int(time.time() - self.recording_start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            self.recording_timer_label.setText(time_str)
            
            # 録音インジケーターウィンドウのタイマーも更新
            self.status_indicator_window.update_timer(time_str)
    
    def start_transcription(self, audio_file=None):
        """Start transcription"""
        self.status_bar.showMessage("文字起こし中...")
        
        # 文字起こし中状態の表示
        if self.show_indicator:
            # 念のため、一度ウィンドウを隠してリセット
            self.status_indicator_window.hide()
            self.status_indicator_window.set_mode(StatusIndicatorWindow.MODE_TRANSCRIBING)
            self.status_indicator_window.show()
        
        # 言語の選択
        selected_language = self.language_combo.currentData()
        
        # バックグラウンドスレッドで文字起こし処理を実行
        if audio_file:
            transcription_thread = threading.Thread(
                target=self.perform_transcription,
                args=(audio_file, selected_language)
            )
            transcription_thread.daemon = True
            transcription_thread.start()
    
    def perform_transcription(self, audio_file, language=None):
        """Perform the actual transcription in a background thread"""
        try:
            # Transcribe the audio
            result = self.whisper_transcriber.transcribe(audio_file, language)
            
            # Emit signal with the result
            self.transcription_complete.emit(result)
            
        except Exception as e:
            # Handle errors
            self.transcription_complete.emit(f"エラー: {str(e)}")
    
    def on_transcription_complete(self, text):
        """Handle completed transcription"""
        # Update the text widget with the transcription result
        self.transcription_text.setPlainText(text)
        
        # 使用したモデル名を取得
        model_id = self.model_combo.currentData()
        model_name = self.model_combo.currentText()
        
        # Update status with model information
        self.status_bar.showMessage(f"文字起こしが完了しました (使用モデル: {model_name})", 3000)
        
        # Auto copy to clipboard if enabled
        if self.auto_copy and text:
            QApplication.clipboard().setText(text)
            self.status_bar.showMessage(f"文字起こしが完了し、クリップボードにコピーしました (使用モデル: {model_name})", 3000)
            
            # コピー完了状態の表示
            if self.show_indicator:
                self.status_indicator_window.set_mode(StatusIndicatorWindow.MODE_COPIED)
                self.status_indicator_window.show()
        else:
            # 自動コピーが無効の場合は、ステータスインジケーターを非表示
            self.status_indicator_window.hide()
        
        # Play complete sound
        self.play_complete_sound()
    
    def copy_to_clipboard(self):
        """Copy transcription to clipboard"""
        text = self.transcription_text.toPlainText()
        QApplication.clipboard().setText(text)
        self.status_bar.showMessage("クリップボードにコピーしました", 2000)
        
        # コピー完了状態の表示
        if self.show_indicator:
            self.status_indicator_window.set_mode(StatusIndicatorWindow.MODE_COPIED)
            self.status_indicator_window.show()
    
    def setup_connections(self):
        """追加の接続設定"""
        # モデル選択が変更されたときのイベント
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)
    
    def on_model_changed(self, index):
        """モデルが変更されたときの処理"""
        model_id = self.model_combo.currentData()
        if model_id and self.whisper_transcriber:
            self.whisper_transcriber.set_model(model_id)
            self.settings.setValue("model", model_id)
            model_name = self.model_combo.currentText()
            self.status_bar.showMessage(f"文字起こしモデルを「{model_name}」に変更しました", 2000)

    def setup_global_hotkey(self):
        """Setup global hotkey"""
        try:
            # まず以前のホットキーの登録を試みる（エラーが出ても続行）
            try:
                keyboard.unhook_all_hotkeys()
            except:
                pass
            
            # 新しいホットキーを登録
            keyboard.add_hotkey(self.hotkey, self.toggle_recording)
            print(f"ホットキー '{self.hotkey}' を設定しました")
            return True
        except Exception as e:
            print(f"ホットキーの設定エラー: {e}")
            # エラーがあってもアプリは正常に動作するようにする
            return False
    
    def setup_system_tray(self):
        """Setup system tray"""
        # アイコンファイルのパスを取得
        icon_path = getResourcePath("assets/icon.ico")
        
        if os.path.exists(icon_path):
            self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
        else:
            # アイコンファイルが見つからない場合は標準アイコンを使用
            self.tray_icon = QSystemTrayIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay), self)
            print(f"警告: システムトレイ用アイコンファイルが見つかりません: {icon_path}")
        
        self.tray_icon.setToolTip("Open Super Whisper")
        
        # Create tray menu
        menu = QMenu()
        
        # Add show/hide action
        show_action = QAction("表示", self)
        show_action.triggered.connect(self.show)
        menu.addAction(show_action)
        
        # Add separator
        menu.addSeparator()
        
        # Add record action
        record_action = QAction("録音開始/停止", self)
        record_action.triggered.connect(self.toggle_recording)
        menu.addAction(record_action)
        
        # Add separator
        menu.addSeparator()
        
        # Add exit action
        exit_action = QAction("終了", self)
        exit_action.triggered.connect(self.quit_application)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    def closeEvent(self, event):
        """Override close event to minimize to tray instead of closing"""
        # Alt+F4 またはシステムのクローズ要求によって呼ばれる
        
        # Alt キーが押されている場合は完全に終了
        if QApplication.keyboardModifiers() == Qt.KeyboardModifier.AltModifier:
            self.quit_application()
            event.accept()
        # 通常の閉じる操作ではトレイに最小化
        elif self.tray_icon.isVisible():
            QMessageBox.information(self, "情報", 
                "アプリケーションはシステムトレイで実行されています。\n"
                "完全に終了するには、トレイアイコンから「終了」を選択するか、\n"
                "ツールバーの「アプリケーション終了」をクリックしてください。")
            self.hide()
            event.ignore()
        else:
            event.accept()
    
    def show_hotkey_dialog(self):
        """Show dialog to set global hotkey"""
        # Unregister current hotkey temporarily
        try:
            keyboard.unhook_all_hotkeys()
        except:
            pass
        
        dialog = HotkeyDialog(self, self.hotkey)
        if dialog.exec():
            new_hotkey = dialog.get_hotkey()
            if new_hotkey:
                self.hotkey = new_hotkey
                self.settings.setValue("hotkey", self.hotkey)
                self.setup_global_hotkey()
                self.status_bar.showMessage(f"ホットキーを {self.hotkey} に設定しました", 3000)
    
    def toggle_auto_copy(self):
        """Toggle auto copy option"""
        self.auto_copy = self.auto_copy_action.isChecked()
        self.settings.setValue("auto_copy", self.auto_copy)
        status = "有効" if self.auto_copy else "無効"
        self.status_bar.showMessage(f"自動コピーを{status}にしました", 2000)
    
    def quit_application(self):
        """アプリケーションを完全に終了する"""
        # トレイアイコンを非表示にする
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        
        # 設定を保存
        self.settings.sync()
        
        # アプリケーションを終了
        QApplication.quit()
    
    def setup_sound_players(self):
        """サウンドプレーヤーの初期化"""
        # 録音開始用サウンドプレーヤー
        self.start_player = QMediaPlayer()
        self.start_audio_output = QAudioOutput()
        self.start_player.setAudioOutput(self.start_audio_output)
        
        # 録音終了用サウンドプレーヤー
        self.stop_player = QMediaPlayer()
        self.stop_audio_output = QAudioOutput()
        self.stop_player.setAudioOutput(self.stop_audio_output)
        
        # 文字起こし完了用サウンドプレーヤー
        self.complete_player = QMediaPlayer()
        self.complete_audio_output = QAudioOutput()
        self.complete_player.setAudioOutput(self.complete_audio_output)
    
    def play_start_sound(self):
        """録音開始サウンドを再生"""
        if not self.enable_sound:
            return
        # assets内の音声ファイルを使用
        sound_path = getResourcePath("assets/start_sound.wav")
        self.start_player.setSource(QUrl.fromLocalFile(sound_path))
        self.start_audio_output.setVolume(0.5)
        self.start_player.play()
    
    def play_stop_sound(self):
        """録音終了サウンドを再生"""
        if not self.enable_sound:
            return
        # assets内の音声ファイルを使用
        sound_path = getResourcePath("assets/stop_sound.wav")
        self.stop_player.setSource(QUrl.fromLocalFile(sound_path))
        self.stop_audio_output.setVolume(0.5)
        self.stop_player.play()
    
    def play_complete_sound(self):
        """文字起こし完了サウンドを再生"""
        if not self.enable_sound:
            return
        # assets内の音声ファイルを使用
        sound_path = getResourcePath("assets/complete_sound.wav")
        self.complete_player.setSource(QUrl.fromLocalFile(sound_path))
        self.complete_audio_output.setVolume(0.5)
        self.complete_player.play()

    def toggle_sound_option(self):
        """通知音のオン/オフを切り替える"""
        self.enable_sound = self.sound_action.isChecked()
        self.settings.setValue("enable_sound", self.enable_sound)
        status = "有効" if self.enable_sound else "無効"
        self.status_bar.showMessage(f"通知音を{status}にしました", 2000)

    def toggle_indicator_option(self):
        """インジケータ表示のオン/オフを切り替える"""
        self.show_indicator = self.indicator_action.isChecked()
        self.settings.setValue("show_indicator", self.show_indicator)
        
        # インジケータが無効になったら非表示にする
        if not self.show_indicator:
            self.status_indicator_window.hide()
            
        status = "表示" if self.show_indicator else "非表示"
        self.status_bar.showMessage(f"状態インジケータを{status}にしました", 2000)


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    
    # アプリケーションアイコンを設定
    icon_path = getResourcePath("assets/icon.ico")
    
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        # アイコンファイルが見つからない場合は標準アイコンを使用
        app_icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        app.setWindowIcon(app_icon)
        print(f"警告: アプリケーション用アイコンファイルが見つかりません: {icon_path}")
    
    # PyQt6ではハイDPIスケーリングはデフォルトで有効
    # 古い属性設定は不要
    
    # Check if QSystemTrayIcon is supported
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "Error", "システムトレイがサポートされていません。")
        sys.exit(1)
    
    # Set quit on last window closed to False to allow minimizing to tray
    app.setQuitOnLastWindowClosed(False)
    
    # Create and show the main window
    window = MainWindow()
    
    # Show notification about hotkey if first run
    settings = QSettings("OpenSuperWhisper", "WhisperTranscriber")
    if not settings.contains("first_run_done"):
        hotkey = settings.value("hotkey", DEFAULT_HOTKEY)
        QMessageBox.information(
            window, 
            "ホットキー情報", 
            f"Open Super Whisperは常にバックグラウンドで実行されています。\n"
            f"グローバルホットキー: {hotkey} で録音を開始/停止できます。\n"
            f"この設定はツールバーの「ホットキー設定」から変更できます。"
        )
        settings.setValue("first_run_done", True)
    
    # Show window (starts minimized to tray by default)
    if '--minimized' in sys.argv or '-m' in sys.argv:
        # Start minimized to tray
        pass
    else:
        window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
