import os
import sys
import time
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon, QStyle
from PyQt6.QtGui import QIcon

from src.gui.main_window import MainWindow, getResourcePath
from src.gui.config import AppConfig
from src.gui.labels import AppLabels

def main():
    """
    アプリケーションのエントリーポイント
    
    アプリケーションの初期化、設定、メインウィンドウの表示を行います。
    コマンドライン引数に応じて、最小化状態で起動することも可能です。
    
    Returns
    -------
    int
        アプリケーションの終了コード
    """
    app = QApplication(sys.argv)
    
    # アプリケーションアイコンを設定
    icon_path = getResourcePath("assets/icon.ico")
    
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        # アイコンファイルが見つからない場合は標準アイコンを使用
        app_icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        app.setWindowIcon(app_icon)
        print(f"Warning: Application icon file not found: {icon_path}")
    
    # PyQt6ではハイDPIスケーリングはデフォルトで有効
    # 古い属性設定は不要
    
    # システムトレイがサポートされているか確認
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, AppLabels.ERROR_TITLE, AppLabels.ERROR_SYSTEM_TRAY)
        sys.exit(1)
    
    # 最後のウィンドウが閉じられてもアプリケーションを終了しない設定
    app.setQuitOnLastWindowClosed(False)
    
    # メインウィンドウの作成と表示
    window = MainWindow()
    
    # 初回起動時はホットキーについての通知を表示
    if not window.settings.contains("first_run_done"):
        hotkey = window.settings.value("hotkey", AppConfig.DEFAULT_HOTKEY)
        QMessageBox.information(
            window, 
            AppLabels.HOTKEY_INFO_TITLE, 
            AppLabels.HOTKEY_INFO_MESSAGE.format(hotkey)
        )
        window.settings.setValue("first_run_done", True)
    
    # ウィンドウを表示（デフォルトではトレイに最小化して起動）
    if '--minimized' in sys.argv or '-m' in sys.argv:
        # トレイに最小化して起動
        pass
    else:
        window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 