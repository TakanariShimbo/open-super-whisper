import os
import sys
import threading
import time
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QComboBox, QFileDialog,
    QCheckBox, QLineEdit, QListWidget, QMessageBox, QSplitter,
    QStatusBar, QToolBar, QDialog, QGridLayout, QFormLayout
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSettings
from PyQt6.QtGui import QIcon, QAction, QFont

from src.core.audio_recorder import AudioRecorder
from src.core.whisper_api import WhisperTranscriber


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
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Open Super Whisper")
        self.setMinimumSize(800, 600)
        
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
        """Create toolbar with actions"""
        toolbar = QToolBar("メインツールバー")
        self.addToolBar(toolbar)
        
        # API key action
        api_key_action = QAction("APIキー", self)
        api_key_action.triggered.connect(self.show_api_key_dialog)
        toolbar.addAction(api_key_action)
        
        # Custom vocabulary action
        vocab_action = QAction("カスタム語彙", self)
        vocab_action.triggered.connect(self.show_vocabulary_dialog)
        toolbar.addAction(vocab_action)
        
        # Copy to clipboard action
        copy_action = QAction("クリップボードにコピー", self)
        copy_action.triggered.connect(self.copy_to_clipboard)
        toolbar.addAction(copy_action)
        
        # Save as text action
        save_action = QAction("テキストとして保存", self)
        save_action.triggered.connect(self.save_transcription)
        toolbar.addAction(save_action)
    
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


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
