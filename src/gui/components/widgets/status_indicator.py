"""
状態表示ウィンドウモジュール

録音中、文字起こし中、コピー完了などの状態を視覚的にユーザーに伝えるためのフローティングウィンドウを提供します
"""

import os
import sys
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QFont

from src.gui.resources.labels import AppLabels
from src.gui.resources.styles import AppStyles

class StatusIndicatorWindow(QWidget):
    """
    アプリケーションの状態を表示する小さなウィンドウ
    
    録音中、文字起こし中、コピー完了などの状態を視覚的に
    ユーザーに伝えるためのフローティングウィンドウです。
    """
    
    # 状態の定義
    MODE_RECORDING = 0
    MODE_TRANSCRIBING = 1
    MODE_TRANSCRIBED = 2
    
    def __init__(self, parent=None):
        """
        StatusIndicatorWindowの初期化
        
        Parameters
        ----------
        parent : QWidget, optional
            親ウィジェット
        """
        super().__init__(parent)
        
        # ウィンドウ設定
        self.setWindowFlags(
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # ウィンドウサイズを調整して見切れを完全に解消
        self.setFixedSize(160, 80)
        
        # メインフレーム（背景用）の作成
        self.status_frame = QFrame(self)
        self.status_frame.setObjectName("statusFrame")
        self.status_frame.setGeometry(0, 0, 160, 80)  # ウィジェットと同じサイズに設定
        
        # レイアウト設定 - マージンを調整して内容が見切れないようにする
        self.layout = QVBoxLayout(self.status_frame)
        self.layout.setContentsMargins(8, 10, 8, 10)
        self.layout.setSpacing(8)
        
        # ステータスラベルは削除し、説明ラベルとタイマーラベルのみを使用
        
        # 説明ラベル - フォントサイズを調整
        self.info_label = QLabel("録音中")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        self.info_label.setObjectName("infoLabel")
        self.layout.addWidget(self.info_label)
        
        # タイマーラベル（録音時間表示用）
        self.timer_label = QLabel("00:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setFont(QFont("Arial", 14))
        self.timer_label.setObjectName("timerLabel")
        self.layout.addWidget(self.timer_label)
        
        # 文字起こし完了時の自動非表示タイマー
        self.auto_hide_timer = QTimer(self)
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.hide)
        
        # スタイルシート設定 - 新しいスタイル適用方法
        self.setStyleSheet(AppStyles.get_recording_indicator_style("normal"))
        
        # 初期状態では非表示に設定
        self.hide()
        
        # 現在のモードを記録する変数
        self.current_mode = None
        
        # ウィンドウの位置を設定
        self.position_window()
        
        # マウスドラッグ用の変数
        self.drag_position = None
        
        # 録音開始時間
        self.recording_start_time = 0
        
        # 録音タイマー
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.update_recording_time)
        
    def set_mode(self, mode):
        """
        表示モードを設定する
        
        Parameters
        ----------
        mode : int
            表示モード（MODE_RECORDING, MODE_TRANSCRIBING, MODE_TRANSCRIBED）
        """
        self.current_mode = mode
        
        if mode == self.MODE_RECORDING:
            # 録音中の表示
            self.info_label.setText("録音中")
            self.timer_label.setVisible(True)
            
            # 録音中のスタイル - 新しいスタイル適用方法
            self.setStyleSheet(AppStyles.get_recording_indicator_style("active"))
            
            # 録音中のタイマーをリセットして開始
            self.recording_start_time = time.time()
            self.update_recording_time()
            self.recording_timer.start(1000)  # 1秒ごとに更新
            
            # 自動的に隠さない
            self.auto_hide_timer.stop()
        
        elif mode == self.MODE_TRANSCRIBING:
            # 文字起こし中の表示
            self.info_label.setText("文字起こし中")
            self.timer_label.setVisible(False)
            
            # 文字起こし中のスタイル - 新しいスタイル適用方法
            self.setStyleSheet(AppStyles.get_recording_indicator_style("transcribing"))
            
            # 録音タイマーを停止
            self.recording_timer.stop()
            
            # 自動的に隠さない
            self.auto_hide_timer.stop()
        
        elif mode == self.MODE_TRANSCRIBED:
            # 文字起こし完了の表示
            self.info_label.setText("文字起こし完了")
            self.timer_label.setVisible(False)
            
            # 文字起こし完了のスタイル - 新しいスタイル適用方法
            self.setStyleSheet(AppStyles.get_recording_indicator_style("transcribed"))
            
            # 録音タイマーを停止
            self.recording_timer.stop()
            
            # 3秒後に自動的に隠す
            self.auto_hide_timer.start(3000)
    
    def position_window(self):
        """
        ウィンドウを画面の右下に配置
        """
        screen_geometry = QApplication.primaryScreen().geometry()
        window_geometry = self.geometry()
        
        # 画面の右下から少し内側に配置
        x = screen_geometry.width() - window_geometry.width() - 20
        y = screen_geometry.height() - window_geometry.height() - 100
        
        self.move(x, y)
    
    def update_recording_time(self):
        """
        録音時間を更新
        """
        elapsed_seconds = int(time.time() - self.recording_start_time)
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def update_timer(self, seconds):
        """
        タイマー表示を外部から更新
        
        Parameters
        ----------
        seconds : int or str
            経過秒数または「MM:SS」形式の時間文字列
        """
        # 文字列形式（"MM:SS"）の場合はそのまま表示
        if isinstance(seconds, str) and ":" in seconds:
            self.timer_label.setText(seconds)
        # 整数値の場合は分:秒形式に変換
        else:
            try:
                # 文字列が渡された場合は整数に変換
                if isinstance(seconds, str):
                    seconds = int(seconds)
                
                minutes = seconds // 60
                seconds = seconds % 60
                self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
            except (ValueError, TypeError):
                # 変換できない場合はそのまま表示（エラー防止）
                if isinstance(seconds, str):
                    self.timer_label.setText(seconds)
                else:
                    self.timer_label.setText("00:00")
    
    def mousePressEvent(self, event):
        """
        ウィンドウのドラッグを可能にする
        
        Parameters
        ----------
        event : QMouseEvent
            マウスイベント
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """
        ウィンドウを移動
        
        Parameters
        ----------
        event : QMouseEvent
            マウスイベント
        """
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

# スタンドアロンでテスト実行時の処理
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # テスト用ウィンドウの作成と表示
    status_window = StatusIndicatorWindow()
    
    # 初期モードを設定
    status_window.set_mode(StatusIndicatorWindow.MODE_RECORDING)
    
    # 画面中央に配置して表示
    status_window.show()
    
    # タイマーでモード切替テスト
    def change_to_transcribing():
        status_window.set_mode(StatusIndicatorWindow.MODE_TRANSCRIBING)
        
    def change_to_transcribed():
        status_window.set_mode(StatusIndicatorWindow.MODE_TRANSCRIBED)
    
    # 3秒後に文字起こし中モードへ
    QTimer.singleShot(3000, change_to_transcribing)
    
    # 6秒後に文字起こし完了モードへ
    QTimer.singleShot(6000, change_to_transcribed)
    
    sys.exit(app.exec()) 