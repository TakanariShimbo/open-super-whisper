"""
状態表示ウィンドウモジュール

録音中、文字起こし中、コピー完了などの状態を視覚的にユーザーに伝えるためのフローティングウィンドウを提供します
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QTimer

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
        
        # 文字起こし完了時の自動非表示タイマー
        self.auto_hide_timer = QTimer(self)
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.hide)
        
        # スタイルシート設定
        self.setStyleSheet(AppStyles.STATUS_INDICATOR_STYLE)
        
        # 初期状態では非表示に設定
        self.hide()
        
        # 現在のモードを記録する変数
        self.current_mode = None
        
        # ウィンドウの位置を設定
        self.position_window()
        
        # マウスドラッグ用の変数
        self.drag_position = None
        
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
            self.status_label.setText(AppLabels.INDICATOR_RECORDING)
            self.setFixedSize(150, 90)
            self.timer_label.setText("00:00")
            self.timer_label.show()
            
            # 録音中のスタイル - 赤系のグラデーション
            self.frame.setStyleSheet(AppStyles.RECORDING_INDICATOR_FRAME_STYLE)
        
        elif mode == self.MODE_TRANSCRIBING:
            self.status_label.setText(AppLabels.INDICATOR_TRANSCRIBING)
            self.setFixedSize(150, 70)
            self.timer_label.setText("")
            self.timer_label.hide()
            
            # 文字起こし中のスタイル - グレー系のグラデーション
            self.frame.setStyleSheet(AppStyles.TRANSCRIBING_INDICATOR_FRAME_STYLE)
        
        elif mode == self.MODE_TRANSCRIBED:
            self.status_label.setText(AppLabels.INDICATOR_TRANSCRIBED)
            self.setFixedSize(150, 70)
            self.timer_label.setText("")
            self.timer_label.hide()
            
            # 文字起こし完了のスタイル - 青系のグラデーション
            self.frame.setStyleSheet(AppStyles.TRANSCRIBED_INDICATOR_FRAME_STYLE)
            
            # 3秒後に非表示
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
    
    def update_timer(self, time_str):
        """
        タイマー表示を更新（録音モード時）
        
        Parameters
        ----------
        time_str : str
            表示する時間文字列
        """
        if self.current_mode == self.MODE_RECORDING:
            self.timer_label.setText(time_str)
        
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