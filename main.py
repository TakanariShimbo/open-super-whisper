#!/usr/bin/env python3
"""
Open Super Whisper - OpenAIのWhisperモデルを使用した音声文字起こし用
Pythonデスクトップアプリケーション

このアプリケーションはOpenAI Whisper APIを使用して音声を録音し、
文字起こしするためのユーザーフレンドリーなインターフェースを提供します。
グローバルホットキーによる録音制御や自動クリップボード連携機能を備えています。
"""

import sys
import os
import argparse
from pathlib import Path

# インポート用にsrcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# メインウィンドウをインポート
from src.gui.main_window import main

if __name__ == "__main__":
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description="Open Super Whisper")
    parser.add_argument("-m", "--minimized", action="store_true", 
                        help="システムトレイに最小化した状態で起動")
    args = parser.parse_args()
    
    # アプリケーションの起動
    if args.minimized:
        sys.argv.append("--minimized")
    main()
