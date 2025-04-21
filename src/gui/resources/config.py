"""
アプリケーションのデフォルト設定値を定義するモジュール

このモジュールには、アプリケーション全体で使用されるデフォルト値が含まれています。
設定値の一元管理により、変更が必要になった場合に簡単に更新できます。
"""

class AppConfig:
    """アプリケーション全体の設定を管理するクラス"""
    
    # アプリケーション設定
    APP_NAME = "OpenSuperWhisper"
    APP_ORGANIZATION = "OpenSuperWhisper"
    
    # 認証設定
    DEFAULT_API_KEY = ""
    
    # 機能設定
    DEFAULT_HOTKEY = "ctrl+shift+r"
    DEFAULT_AUTO_COPY = True
    DEFAULT_ENABLE_SOUND = True
    DEFAULT_SHOW_INDICATOR = True
    DEFAULT_MODEL = "gpt-4o-transcribe"
    
    # 言語設定
    DEFAULT_LANGUAGE = ""  # 空文字列は自動検出を意味する
    
    # サウンドファイルパス
    START_SOUND_PATH = "assets/start_sound.wav"
    STOP_SOUND_PATH = "assets/stop_sound.wav"
    COMPLETE_SOUND_PATH = "assets/complete_sound.wav" 