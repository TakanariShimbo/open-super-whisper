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
    QSystemTrayIcon, QMenu, QStyle
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
        
        # サウンドプレーヤーの初期化
        self.setup_sound_players()
        
        # Initialize components
        self.audio_recorder = AudioRecorder()
        
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
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Create toolbar
        self.create_toolbar()
        
        # Control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout()
        
        # Recording controls
        self.record_button = QPushButton("録音開始")
        self.record_button.clicked.connect(self.toggle_recording)
        
        self.import_button = QPushButton("音声ファイル読込")
        self.import_button.clicked.connect(self.import_audio)
        
        # Language selection
        language_layout = QHBoxLayout()
        language_layout.addWidget(QLabel("言語:"))
        self.language_combo = QComboBox()
        language_layout.addWidget(self.language_combo)
        
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
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("モデル:"))
        self.model_combo = QComboBox()
        model_layout.addWidget(self.model_combo)
        
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
        
        # Add controls to layout
        control_layout.addWidget(self.record_button)
        control_layout.addWidget(self.import_button)
        control_layout.addLayout(language_layout)
        control_layout.addLayout(model_layout)
        
        control_panel.setLayout(control_layout)
        main_layout.addWidget(control_panel)
        
        # Transcription output
        self.transcription_text = QTextEdit()
        self.transcription_text.setPlaceholderText("ここに文字起こしが表示されます...")
        self.transcription_text.setReadOnly(False)  # Allow editing for corrections
        
        main_layout.addWidget(self.transcription_text)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("準備完了")
        
        # Recording indicator
        self.recording_indicator = QLabel("●")
        self.recording_indicator.setStyleSheet("color: gray;")
        self.recording_timer_label = QLabel("00:00")
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
        
        # Copy to clipboard action
        copy_action = QAction("クリップボードにコピー", self)
        copy_action.triggered.connect(self.copy_to_clipboard)
        toolbar.addAction(copy_action)
        
        # Save as text action
        save_action = QAction("テキストとして保存", self)
        save_action.triggered.connect(self.save_transcription)
        toolbar.addAction(save_action)
        
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
        
        # Play stop sound
        self.play_stop_sound()
    
    def update_recording_status(self, is_recording):
        """Update the recording indicator"""
        if is_recording:
            self.recording_indicator.setStyleSheet("color: red;")
        else:
            self.recording_indicator.setStyleSheet("color: gray;")
    
    def update_recording_time(self):
        """Update the recording time display"""
        if self.audio_recorder.is_recording():
            elapsed = int(time.time() - self.recording_start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.recording_timer_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def import_audio(self):
        """Import audio file for transcription"""
        if not self.whisper_transcriber:
            QMessageBox.warning(self, "エラー", "先にAPIキーを設定してください")
            return
            
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "音声ファイル読込",
            "",
            "音声ファイル (*.mp3 *.wav *.m4a *.ogg *.flac);;すべてのファイル (*)"
        )
        
        if file_path:
            self.status_bar.showMessage(f"{os.path.basename(file_path)}を処理中...")
            
            # Convert file if needed
            audio_file = self.audio_recorder.load_audio_file(file_path)
            if audio_file:
                self.start_transcription(audio_file)
            else:
                self.status_bar.showMessage("音声ファイルの処理中にエラーが発生しました", 3000)
    
    def start_transcription(self, audio_file):
        """Start transcription in a separate thread"""
        if not self.whisper_transcriber:
            QMessageBox.warning(self, "エラー", "先にAPIキーを設定してください")
            return
            
        # Get selected language or empty string for auto-detection
        selected_language = self.language_combo.currentData()
        
        # 選択されたモデルを設定
        selected_model = self.model_combo.currentData()
        self.whisper_transcriber.set_model(selected_model)
        
        # Start transcription in a thread
        threading.Thread(
            target=self.perform_transcription,
            args=(audio_file, selected_language),
            daemon=True
        ).start()
    
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
        
        # Play complete sound
        self.play_complete_sound()
    
    def copy_to_clipboard(self):
        """Copy transcription to clipboard"""
        text = self.transcription_text.toPlainText()
        QApplication.clipboard().setText(text)
        self.status_bar.showMessage("クリップボードにコピーしました", 2000)
    
    def save_transcription(self):
        """Save transcription to a text file"""
        text = self.transcription_text.toPlainText()
        if not text:
            return
            
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self,
            "文字起こしを保存",
            f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "テキストファイル (*.txt);;すべてのファイル (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.status_bar.showMessage(f"{os.path.basename(file_path)}に保存しました", 3000)
            except Exception as e:
                QMessageBox.warning(self, "保存エラー", f"ファイル保存中にエラーが発生しました: {e}")
    
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
