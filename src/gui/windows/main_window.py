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
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSettings, QUrl, QObject
from PyQt6.QtGui import QIcon, QAction, QFont
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import keyboard

from src.core.audio_recorder import AudioRecorder
from src.core.whisper_api import WhisperTranscriber
from src.gui.resources.config import AppConfig
from src.gui.resources.labels import AppLabels
from src.gui.resources.styles import AppStyles
from src.gui.components.dialogs.api_key_dialog import APIKeyDialog
from src.gui.components.dialogs.vocabulary_dialog import VocabularyDialog
from src.gui.components.dialogs.system_instructions_dialog import SystemInstructionsDialog
from src.gui.components.dialogs.hotkey_dialog import HotkeyDialog
from src.gui.components.widgets.status_indicator import StatusIndicatorWindow
from src.gui.utils.resource_helper import getResourcePath

class MainWindow(QMainWindow):
    """
    アプリケーションのメインウィンドウ
    
    ユーザーインターフェース、音声録音機能、文字起こし機能を統合した
    アプリケーションの中心となるウィンドウです。
    """
    
    # カスタムシグナルの定義
    transcription_complete = pyqtSignal(str)
    recording_status_changed = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        
        # 設定の読み込み
        self.settings = QSettings(AppConfig.APP_ORGANIZATION, AppConfig.APP_NAME)
        self.api_key = self.settings.value("api_key", AppConfig.DEFAULT_API_KEY)
        
        # ホットキーとクリップボード設定
        self.hotkey = self.settings.value("hotkey", AppConfig.DEFAULT_HOTKEY)
        self.auto_copy = self.settings.value("auto_copy", AppConfig.DEFAULT_AUTO_COPY, type=bool)
        
        # サウンド設定
        self.enable_sound = self.settings.value("enable_sound", AppConfig.DEFAULT_ENABLE_SOUND, type=bool)
        
        # インジケータ表示設定（デフォルトON）
        self.show_indicator = self.settings.value("show_indicator", AppConfig.DEFAULT_SHOW_INDICATOR, type=bool)
        
        # サウンドプレーヤーの初期化
        self.setup_sound_players()
        
        # コンポーネントの初期化
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
        
        # UIの設定
        self.init_ui()
        
        # シグナルの接続
        self.transcription_complete.connect(self.on_transcription_complete)
        self.recording_status_changed.connect(self.update_recording_status)
        
        # APIキーの確認
        if not self.api_key:
            self.show_api_key_dialog()
            
        # 追加の接続設定
        self.setup_connections()
        
        # グローバルホットキーの設定
        self.setup_global_hotkey()
        
        # システムトレイの設定
        self.setup_system_tray()
    
    def init_ui(self):
        """
        ユーザーインターフェースを初期化する
        
        ウィンドウのサイズ、タイトル、スタイル、レイアウト、
        およびウィジェットの配置を設定します。
        """
        self.setWindowTitle(AppLabels.APP_TITLE)
        self.setMinimumSize(1000, 600)
        self.setFixedSize(1000, 600)  # ウィンドウサイズを固定
        
        # アプリケーションアイコンを設定
        icon_path = getResourcePath("assets/icon.ico")
        
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # アイコンファイルが見つからない場合は標準アイコンを使用
            self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            print(f"Warning: Icon file not found: {icon_path}")
            
        # アプリ全体のスタイルを設定
        self.setStyleSheet(AppStyles.MAIN_WINDOW_STYLE)
        
        # 中央ウィジェットとメインレイアウトの作成
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # ツールバーの作成
        self.create_toolbar()
        
        # コントロールパネル
        control_panel = QWidget()
        control_panel.setObjectName("controlPanel")
        control_panel.setStyleSheet(AppStyles.CONTROL_PANEL_STYLE)
        control_layout = QGridLayout()
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(12)
        
        # 録音コントロール
        self.record_button = QPushButton(AppLabels.RECORD_START_BUTTON)
        self.record_button.setObjectName("recordButton")
        self.record_button.setMinimumHeight(40)
        self.record_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.record_button.setStyleSheet(AppStyles.RECORD_BUTTON_STYLE)
        self.record_button.clicked.connect(self.toggle_recording)
        
        # コントロールフォーム
        control_form = QWidget()
        form_layout = QFormLayout(control_form)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(10)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # 言語選択
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("languageCombo")
        
        # 言語オプションの追加
        self.language_combo.addItem(AppLabels.AUTO_DETECT, "")
        self.language_combo.addItem(AppLabels.LANGUAGE_ENGLISH, "en")
        self.language_combo.addItem(AppLabels.LANGUAGE_SPANISH, "es")
        self.language_combo.addItem(AppLabels.LANGUAGE_FRENCH, "fr")
        self.language_combo.addItem(AppLabels.LANGUAGE_GERMAN, "de")
        self.language_combo.addItem(AppLabels.LANGUAGE_ITALIAN, "it")
        self.language_combo.addItem(AppLabels.LANGUAGE_PORTUGUESE, "pt")
        self.language_combo.addItem(AppLabels.LANGUAGE_JAPANESE, "ja")
        self.language_combo.addItem(AppLabels.LANGUAGE_KOREAN, "ko")
        self.language_combo.addItem(AppLabels.LANGUAGE_CHINESE, "zh")
        self.language_combo.addItem(AppLabels.LANGUAGE_RUSSIAN, "ru")
        
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
        last_model = self.settings.value("model", AppConfig.DEFAULT_MODEL)
        index = self.model_combo.findData(last_model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
            
        # フォームにフィールドを追加
        language_label = QLabel(AppLabels.LANGUAGE_LABEL)
        language_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        model_label = QLabel(AppLabels.MODEL_LABEL)
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
        
        # 文字起こしパネル
        transcription_panel = QWidget()
        transcription_panel.setObjectName("transcriptionPanel")
        transcription_panel.setStyleSheet(AppStyles.TRANSCRIPTION_PANEL_STYLE)
        
        transcription_layout = QVBoxLayout(transcription_panel)
        transcription_layout.setContentsMargins(15, 15, 15, 15)
        
        # タイトルラベル
        title_label = QLabel(AppLabels.TRANSCRIPTION_TITLE)
        title_label.setObjectName("sectionTitle")
        title_label.setStyleSheet(AppStyles.TRANSCRIPTION_TITLE_STYLE)
        transcription_layout.addWidget(title_label)
        
        # 文字起こし出力
        self.transcription_text = QTextEdit()
        self.transcription_text.setPlaceholderText(AppLabels.TRANSCRIPTION_PLACEHOLDER)
        self.transcription_text.setReadOnly(False)  # 編集できるように設定
        self.transcription_text.setMinimumHeight(250)
        self.transcription_text.setStyleSheet(AppStyles.TRANSCRIPTION_TEXT_STYLE)
        
        transcription_layout.addWidget(self.transcription_text)
        main_layout.addWidget(transcription_panel, 1)
        
        # ステータスバー
        self.status_bar = self.statusBar()
        self.status_bar.showMessage(AppLabels.STATUS_READY)
        self.status_bar.setStyleSheet(AppStyles.STATUS_BAR_STYLE)
        
        # 録音インジケーター
        self.recording_indicator = QLabel("●")
        self.recording_indicator.setObjectName("recordingIndicator")
        self.recording_indicator.setStyleSheet(AppStyles.RECORDING_INDICATOR_NORMAL_STYLE)
        
        self.recording_timer_label = QLabel("00:00")
        self.recording_timer_label.setObjectName("recordingTimerLabel")
        self.recording_timer_label.setStyleSheet(AppStyles.RECORDING_TIMER_LABEL_STYLE)
        
        self.status_bar.addPermanentWidget(self.recording_indicator)
        self.status_bar.addPermanentWidget(self.recording_timer_label)
        
        # 録音タイマーのセットアップ
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.update_recording_time)
        self.recording_start_time = 0
        
        # レイアウトの完了
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def create_toolbar(self):
        """
        アクション付きツールバーを作成する
        
        アプリケーションの主要機能にアクセスするためのツールバーボタンを設定します。
        """
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # APIキーアクション
        api_key_action = QAction(AppLabels.API_KEY_SETTINGS, self)
        api_key_action.triggered.connect(self.show_api_key_dialog)
        toolbar.addAction(api_key_action)
        
        # カスタム語彙アクション
        vocabulary_action = QAction(AppLabels.CUSTOM_VOCABULARY, self)
        vocabulary_action.triggered.connect(self.show_vocabulary_dialog)
        toolbar.addAction(vocabulary_action)
        
        # システム指示アクション
        system_instructions_action = QAction(AppLabels.SYSTEM_INSTRUCTIONS, self)
        system_instructions_action.triggered.connect(self.show_system_instructions_dialog)
        toolbar.addAction(system_instructions_action)
        
        # クリップボードにコピーアクション
        copy_action = QAction(AppLabels.COPY_TO_CLIPBOARD, self)
        copy_action.triggered.connect(self.copy_to_clipboard)
        toolbar.addAction(copy_action)
        
        # セパレーター追加
        toolbar.addSeparator()
        
        # グローバルホットキー設定
        hotkey_action = QAction(AppLabels.HOTKEY_SETTINGS, self)
        hotkey_action.triggered.connect(self.show_hotkey_dialog)
        toolbar.addAction(hotkey_action)
        
        # 自動コピーオプション
        self.auto_copy_action = QAction(AppLabels.AUTO_COPY, self)
        self.auto_copy_action.setCheckable(True)
        self.auto_copy_action.setChecked(self.auto_copy)
        self.auto_copy_action.triggered.connect(self.toggle_auto_copy)
        toolbar.addAction(self.auto_copy_action)
        
        # サウンドオプション
        self.sound_action = QAction(AppLabels.SOUND_NOTIFICATION, self)
        self.sound_action.setCheckable(True)
        self.sound_action.setChecked(self.enable_sound)
        self.sound_action.triggered.connect(self.toggle_sound_option)
        toolbar.addAction(self.sound_action)
        
        # インジケータ表示オプション
        self.indicator_action = QAction(AppLabels.STATUS_INDICATOR, self)
        self.indicator_action.setCheckable(True)
        self.indicator_action.setChecked(self.show_indicator)
        self.indicator_action.triggered.connect(self.toggle_indicator_option)
        toolbar.addAction(self.indicator_action)
        
        # セパレーター追加
        toolbar.addSeparator()
        
        # 終了アクション
        exit_action = QAction(AppLabels.EXIT_APP, self)
        exit_action.triggered.connect(self.quit_application)
        exit_action.setShortcut("Alt+F4")  # 終了ショートカットを追加
        toolbar.addAction(exit_action)
    
    def show_api_key_dialog(self):
        """
        OpenAI APIキー入力ダイアログを表示する
        
        APIキーの入力、保存、検証を行うダイアログを表示します。
        """
        dialog = APIKeyDialog(self, self.api_key)
        if dialog.exec():
            self.api_key = dialog.get_api_key()
            self.settings.setValue("api_key", self.api_key)
            
            # 新しいAPIキーでトランスクライバーを再初期化
            try:
                self.whisper_transcriber = WhisperTranscriber(api_key=self.api_key)
                self.status_bar.showMessage(AppLabels.STATUS_API_KEY_SAVED, 3000)
            except ValueError as e:
                self.whisper_transcriber = None
                QMessageBox.warning(self, AppLabels.ERROR_TITLE, AppLabels.ERROR_API_KEY_MISSING)
    
    def show_vocabulary_dialog(self):
        """
        カスタム語彙管理ダイアログを表示する
        
        文字起こしの精度向上のためのカスタム語彙を管理するダイアログを表示します。
        """
        if not self.whisper_transcriber:
            QMessageBox.warning(self, AppLabels.ERROR_TITLE, AppLabels.ERROR_API_KEY_REQUIRED)
            return
            
        vocabulary = self.whisper_transcriber.get_custom_vocabulary()
        dialog = VocabularyDialog(self, vocabulary)
        
        if dialog.exec():
            new_vocabulary = dialog.get_vocabulary()
            self.whisper_transcriber.clear_custom_vocabulary()
            self.whisper_transcriber.add_custom_vocabulary(new_vocabulary)
            self.status_bar.showMessage(AppLabels.STATUS_VOCABULARY_ADDED.format(len(new_vocabulary)), 3000)
    
    def show_system_instructions_dialog(self):
        """システム指示を管理するダイアログを表示"""
        if not self.whisper_transcriber:
            QMessageBox.warning(self, AppLabels.ERROR_TITLE, AppLabels.ERROR_API_KEY_REQUIRED)
            return
            
        instructions = self.whisper_transcriber.get_system_instructions()
        dialog = SystemInstructionsDialog(self, instructions)
        
        if dialog.exec():
            new_instructions = dialog.get_instructions()
            self.whisper_transcriber.clear_system_instructions()
            self.whisper_transcriber.add_system_instruction(new_instructions)
            self.status_bar.showMessage(AppLabels.STATUS_INSTRUCTIONS_SET.format(len(new_instructions)), 3000)
    
    def toggle_recording(self):
        """
        録音の開始/停止を切り替える
        
        現在の録音状態に応じて、録音を開始または停止します。
        """
        # GUIスレッドでの実行を保証するためQTimer.singleShotを使用
        QTimer.singleShot(0, self._toggle_recording_impl)
    
    def _toggle_recording_impl(self):
        """
        実際の録音切り替え処理の実装
        
        録音の状態を確認し、録音の開始または停止を行います。
        """
        if self.audio_recorder.is_recording():
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """
        音声録音を開始する
        
        録音を開始し、UIの状態を更新します。録音中はタイマーを表示し、
        インジケーターウィンドウを表示します。
        """
        if not self.whisper_transcriber:
            QMessageBox.warning(self, AppLabels.ERROR_TITLE, AppLabels.ERROR_API_KEY_REQUIRED)
            return
            
        self.record_button.setText(AppLabels.RECORD_STOP_BUTTON)
        self.audio_recorder.start_recording()
        self.recording_status_changed.emit(True)
        
        # 録音タイマー開始
        self.recording_start_time = time.time()
        self.recording_timer.start(1000)  # 1秒ごとに更新
        
        # 録音中状態の表示
        if self.show_indicator:
            # 念のため、一度ウィンドウを隠してリセット
            self.status_indicator_window.hide()
            self.status_indicator_window.set_mode(StatusIndicatorWindow.MODE_RECORDING)
            self.status_indicator_window.show()
        
        self.status_bar.showMessage(AppLabels.STATUS_RECORDING)
        
        # 開始音を再生
        self.play_start_sound()
    
    def stop_recording(self):
        """
        録音を停止し文字起こしを開始する
        
        録音を停止して一時ファイルを保存し、文字起こし処理を開始します。
        UIの状態も適切に更新します。
        """
        self.record_button.setText(AppLabels.RECORD_START_BUTTON)
        audio_file = self.audio_recorder.stop_recording()
        self.recording_status_changed.emit(False)
        
        # 録音タイマー停止
        self.recording_timer.stop()
        
        if audio_file:
            self.status_bar.showMessage(AppLabels.STATUS_TRANSCRIBING)
            self.start_transcription(audio_file)
        else:
            # 録音ファイルが作成されなかった場合は状態表示を非表示
            self.status_indicator_window.hide()
        
        # 停止音を再生
        self.play_stop_sound()
    
    def update_recording_status(self, is_recording):
        """
        録音インジケーターの状態を更新する
        
        Parameters
        ----------
        is_recording : bool
            録音中かどうかのフラグ
        
        録音状態に応じてUIの録音インジケーターとボタンのスタイルを更新します。
        """
        if is_recording:
            self.recording_indicator.setStyleSheet(AppStyles.RECORDING_INDICATOR_ACTIVE_STYLE)
            
            # 録音ボタンのスタイルも変更
            self.record_button.setStyleSheet(AppStyles.RECORD_BUTTON_RECORDING_STYLE)
        else:
            self.recording_indicator.setStyleSheet(AppStyles.RECORDING_INDICATOR_INACTIVE_STYLE)
            
            # 録音ボタンのスタイルを元に戻す
            self.record_button.setStyleSheet(AppStyles.RECORD_BUTTON_STYLE)
    
    def update_recording_time(self):
        """
        録音時間表示を更新する
        
        録音中の経過時間を計算し、タイマー表示を更新します。
        インジケーターウィンドウのタイマー表示も同時に更新します。
        """
        if self.audio_recorder.is_recording():
            elapsed = int(time.time() - self.recording_start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            self.recording_timer_label.setText(time_str)
            
            # 録音インジケーターウィンドウのタイマーも更新
            self.status_indicator_window.update_timer(time_str)
    
    def start_transcription(self, audio_file=None):
        """
        文字起こしを開始する
        
        Parameters
        ----------
        audio_file : str, optional
            文字起こしを行う音声ファイルのパス
        
        録音した音声ファイルの文字起こしを開始し、UIの状態を更新します。
        """
        self.status_bar.showMessage(AppLabels.STATUS_TRANSCRIBING)
        
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
        """
        バックグラウンドスレッドで文字起こし処理を実行する
        
        Parameters
        ----------
        audio_file : str
            文字起こしを行う音声ファイルのパス
        language : str, optional
            文字起こしの言語コード
        
        WhisperTranscriberを使用して実際の文字起こし処理を行い、結果を
        シグナルで通知します。エラー発生時も適切にハンドリングします。
        """
        try:
            # 音声を文字起こし
            result = self.whisper_transcriber.transcribe(audio_file, language)
            
            # 結果でシグナルを発信
            self.transcription_complete.emit(result)
            
        except Exception as e:
            # エラー処理
            self.transcription_complete.emit(AppLabels.ERROR_TRANSCRIPTION.format(str(e)))
    
    def on_transcription_complete(self, text):
        """
        文字起こし完了時の処理
        
        Parameters
        ----------
        text : str
            文字起こし結果のテキスト
        
        文字起こし結果をテキストウィジェットに表示し、設定に応じて
        クリップボードにコピーします。また、完了サウンドを再生します。
        """
        # 文字起こし結果でテキストウィジェットを更新
        self.transcription_text.setPlainText(text)
        
        # 使用したモデル名を取得
        model_id = self.model_combo.currentData()
        model_name = self.model_combo.currentText()
        
        # 文字起こし完了状態の表示
        if self.show_indicator:
            self.status_indicator_window.set_mode(StatusIndicatorWindow.MODE_TRANSCRIBED)
            self.status_indicator_window.show()
        
        # 有効な場合は自動でクリップボードにコピー
        if self.auto_copy and text:
            QApplication.clipboard().setText(text)
            self.status_bar.showMessage(AppLabels.STATUS_TRANSCRIBED_COPIED + f" (使用モデル: {model_name})", 3000)
        else:
            # 自動コピーが無効の場合でもモデル情報でステータスを更新
            self.status_bar.showMessage(AppLabels.STATUS_TRANSCRIBED + f" (使用モデル: {model_name})", 3000)
        
        # 完了音を再生
        self.play_complete_sound()
    
    def copy_to_clipboard(self):
        """
        文字起こし結果をクリップボードにコピーする
        
        現在のテキストウィジェットの内容をクリップボードにコピーし、
        ユーザーに通知します。
        """
        text = self.transcription_text.toPlainText()
        QApplication.clipboard().setText(text)
        self.status_bar.showMessage(AppLabels.STATUS_COPIED, 2000)
        
        # 手動コピー時はインジケータを表示しない
    
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
            self.status_bar.showMessage(AppLabels.STATUS_MODEL_CHANGED.format(model_name), 2000)

    def setup_global_hotkey(self):
        """
        グローバルホットキーを設定する
        
        Returns
        -------
        bool
            ホットキー設定の成功・失敗
        
        アプリケーション全体で使用するグローバルホットキーを設定します。
        エラーが発生しても、アプリケーションは引き続き動作します。
        """
        try:
            # まず以前のホットキーの登録を解除
            try:
                keyboard.unhook_all_hotkeys()
                print("All existing hotkeys have been unregistered")
            except Exception as e:
                print(f"Error occurred while unregistering existing hotkeys: {e}")
            
            # クリーンな状態でホットキーを再登録
            keyboard.add_hotkey(self.hotkey, self.toggle_recording, suppress=False)
            print(f"Hotkey '{self.hotkey}' has been set")
            
            # 定期的にホットキー登録状態を確認するタイマーを設定
            self.hotkey_check_timer = QTimer(self)
            self.hotkey_check_timer.timeout.connect(self.check_hotkey_status)
            self.hotkey_check_timer.start(60000)  # 1分ごとにチェック
            
            return True
        except Exception as e:
            print(f"Hotkey setup error: {e}")
            # エラーメッセージをユーザーに表示
            self.status_bar.showMessage(AppLabels.ERROR_HOTKEY.format(e), 5000)
            # エラーがあってもアプリは正常に動作するようにする
            return False
    
    def check_hotkey_status(self):
        """
        ホットキーの状態を定期的にチェックし、必要に応じて再登録を試みる
        """
        try:
            # ホットキーが機能しているか確認できないため、
            # 安全のため定期的に再登録する
            keyboard.unhook_all_hotkeys()
            keyboard.add_hotkey(self.hotkey, self.toggle_recording, suppress=False)
            print("Hotkey has been re-registered")
        except Exception as e:
            print(f"Error during hotkey re-registration: {e}")
    
    def setup_system_tray(self):
        """
        システムトレイアイコンとメニューの設定
        
        システムトレイアイコンを初期化し、右クリックで表示されるコンテキストメニューを
        設定します。メニューには、アプリケーションの表示、録音開始/停止、終了オプションが
        含まれます。
        """
        # アイコンファイルのパスを取得
        icon_path = getResourcePath("assets/icon.ico")
        
        if os.path.exists(icon_path):
            self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
        else:
            # アイコンファイルが見つからない場合は標準アイコンを使用
            self.tray_icon = QSystemTrayIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay), self)
            print(f"Warning: System tray icon file not found: {icon_path}")
        
        self.tray_icon.setToolTip(AppLabels.APP_TITLE)
        
        # トレイメニューをスタイル付きで作成
        menu = QMenu()
        menu.setStyleSheet(AppStyles.SYSTEM_TRAY_MENU_STYLE)
        
        # 表示/非表示アクションを追加
        show_action = QAction(AppLabels.TRAY_SHOW, self)
        show_action.triggered.connect(self.show)
        menu.addAction(show_action)
        
        # セパレーターを追加
        menu.addSeparator()
        
        # 録音アクションを追加
        record_action = QAction(AppLabels.TRAY_RECORD, self)
        record_action.triggered.connect(self.toggle_recording)
        menu.addAction(record_action)
        
        # セパレーターを追加
        menu.addSeparator()
        
        # 終了アクションを追加
        exit_action = QAction(AppLabels.TRAY_EXIT, self)
        exit_action.triggered.connect(self.quit_application)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """
        トレイアイコンがアクティブ化されたときの処理
        
        Parameters
        ----------
        reason : QSystemTrayIcon.ActivationReason
            アクティブ化の理由
        
        トレイアイコンがクリックされたときに、ウィンドウの表示/非表示を切り替えます。
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    def closeEvent(self, event):
        """
        ウィンドウの閉じるイベントを処理する
        
        Parameters
        ----------
        event : QCloseEvent
            閉じるイベント
        
        ウィンドウの閉じるボタンが押されたときの処理を行います。
        Alt+F4で完全終了、それ以外はトレイに最小化します。
        """
        # Alt+F4 またはシステムのクローズ要求によって呼ばれる
        
        # Alt キーが押されている場合は完全に終了
        if QApplication.keyboardModifiers() == Qt.KeyboardModifier.AltModifier:
            self.quit_application()
            event.accept()
        # 通常の閉じる操作ではトレイに最小化
        elif self.tray_icon.isVisible():
            QMessageBox.information(self, AppLabels.INFO_TITLE, 
                AppLabels.INFO_TRAY_MINIMIZED)
            self.hide()
            event.ignore()
        else:
            event.accept()
    
    def show_hotkey_dialog(self):
        """
        グローバルホットキー設定ダイアログを表示する
        
        ホットキーの設定を変更するためのダイアログを表示します。
        ダイアログ表示中は現在のホットキーを一時的に解除します。
        """
        # 現在のホットキーを一時的に解除
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
                self.status_bar.showMessage(AppLabels.STATUS_HOTKEY_SET.format(self.hotkey), 3000)
    
    def toggle_auto_copy(self):
        """
        自動コピー機能のオン/オフを切り替える
        
        文字起こし完了時の自動クリップボードコピー機能の有効/無効を
        切り替え、設定を保存します。
        """
        self.auto_copy = self.auto_copy_action.isChecked()
        self.settings.setValue("auto_copy", self.auto_copy)
        if self.auto_copy:
            self.status_bar.showMessage(AppLabels.STATUS_AUTO_COPY_ENABLED, 2000)
        else:
            self.status_bar.showMessage(AppLabels.STATUS_AUTO_COPY_DISABLED, 2000)
    
    def quit_application(self):
        """
        アプリケーションを完全に終了する
        
        トレイアイコンを非表示にし、設定を保存してからアプリケーションを終了します。
        """
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
        """
        録音開始サウンドを再生する
        
        enable_soundがTrueの場合のみ再生します
        """
        if not self.enable_sound:
            return
        # assets内の音声ファイルを使用
        sound_path = getResourcePath(AppConfig.START_SOUND_PATH)
        self.start_player.setSource(QUrl.fromLocalFile(sound_path))
        self.start_audio_output.setVolume(0.5)
        self.start_player.play()
    
    def play_stop_sound(self):
        """
        録音終了サウンドを再生する
        
        enable_soundがTrueの場合のみ再生します
        """
        if not self.enable_sound:
            return
        # assets内の音声ファイルを使用
        sound_path = getResourcePath(AppConfig.STOP_SOUND_PATH)
        self.stop_player.setSource(QUrl.fromLocalFile(sound_path))
        self.stop_audio_output.setVolume(0.5)
        self.stop_player.play()
    
    def play_complete_sound(self):
        """
        文字起こし完了サウンドを再生する
        
        enable_soundがTrueの場合のみ再生します
        """
        if not self.enable_sound:
            return
        # assets内の音声ファイルを使用
        sound_path = getResourcePath(AppConfig.COMPLETE_SOUND_PATH)
        self.complete_player.setSource(QUrl.fromLocalFile(sound_path))
        self.complete_audio_output.setVolume(0.5)
        self.complete_player.play()

    def toggle_sound_option(self):
        """
        通知音のオン/オフを切り替える
        
        設定を保存し、状態をステータスバーに表示します
        """
        self.enable_sound = self.sound_action.isChecked()
        self.settings.setValue("enable_sound", self.enable_sound)
        if self.enable_sound:
            self.status_bar.showMessage(AppLabels.STATUS_SOUND_ENABLED, 2000)
        else:
            self.status_bar.showMessage(AppLabels.STATUS_SOUND_DISABLED, 2000)

    def toggle_indicator_option(self):
        """
        インジケータ表示のオン/オフを切り替える
        
        設定を保存し、状態をステータスバーに表示します
        """
        self.show_indicator = self.indicator_action.isChecked()
        self.settings.setValue("show_indicator", self.show_indicator)
        
        # インジケータが無効になったら非表示にする
        if not self.show_indicator:
            self.status_indicator_window.hide()
            
        if self.show_indicator:
            self.status_bar.showMessage(AppLabels.STATUS_INDICATOR_SHOWN, 2000)
        else:
            self.status_bar.showMessage(AppLabels.STATUS_INDICATOR_HIDDEN, 2000)
