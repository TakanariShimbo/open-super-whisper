"""
グローバルホットキー管理モジュール

アプリケーション全体で使用するグローバルホットキーの登録・管理機能を提供します。
異なるUIフレームワークでも使用できるよう、コア機能として実装しています。
"""

import os
import sys
from typing import Dict, Callable, Optional, Union, List, Tuple
from pynput import keyboard

class HotkeyManager:
    """
    グローバルホットキーの登録と管理を行うクラス
    
    このクラスは、アプリケーションでグローバルホットキーを設定し管理するための
    中心的な機能を提供します。pynputライブラリを使用してOS全体でのホットキー検出を実現します。
    
    Attributes
    ----------
    hotkeys : dict
        登録されたホットキーとそのコールバック関数のマッピング
    listener : keyboard.GlobalHotKeys
        キーボードイベントをリッスンするリスナーオブジェクト
    """
    
    def __init__(self):
        """HotkeyManagerの初期化"""
        self.hotkeys = {}
        self.listener = None
    
    def register_hotkey(self, hotkey_str: str, callback: Callable[[], None]) -> bool:
        """
        新しいホットキーを登録する
        
        Parameters
        ----------
        hotkey_str : str
            'ctrl+shift+r'のような形式のホットキー文字列
        callback : Callable[[], None]
            ホットキーが押されたときに実行する関数
            
        Returns
        -------
        bool
            登録の成功・失敗
        """
        try:
            # 以前のリスナーがあれば停止
            self.stop_listener()
            
            # ホットキーの組み合わせを解析
            hotkey_combination = self.parse_hotkey_string(hotkey_str)
            if not hotkey_combination:
                raise ValueError(f"Invalid hotkey format: {hotkey_str}")
            
            # 既存のホットキーマップに新しいホットキーを追加または更新
            self.hotkeys[hotkey_combination] = callback
            
            # 新しいリスナーを開始
            return self.start_listener()
        except Exception as e:
            print(f"Failed to register hotkey: {e}")
            return False
    
    def unregister_hotkey(self, hotkey_str: str) -> bool:
        """
        既存のホットキー登録を解除する
        
        Parameters
        ----------
        hotkey_str : str
            解除するホットキーの文字列表現
            
        Returns
        -------
        bool
            解除の成功・失敗
        """
        try:
            # ホットキーの組み合わせを解析
            hotkey_combination = self.parse_hotkey_string(hotkey_str)
            
            # ホットキーが登録されていない場合
            if not hotkey_combination or hotkey_combination not in self.hotkeys:
                return False
            
            # リスナーを停止
            self.stop_listener()
            
            # ホットキーをマップから削除
            del self.hotkeys[hotkey_combination]
            
            # 他のホットキーがまだ残っていれば、リスナーを再開
            if self.hotkeys:
                return self.start_listener()
            
            return True
        except Exception as e:
            print(f"Failed to unregister hotkey: {e}")
            return False
    
    def start_listener(self) -> bool:
        """
        ホットキーリスナーを開始する
        
        Returns
        -------
        bool
            リスナー開始の成功・失敗
        """
        try:
            if not self.hotkeys:
                return False
                
            self.listener = keyboard.GlobalHotKeys(self.hotkeys)
            self.listener.start()
            return True
        except Exception as e:
            print(f"Failed to start hotkey listener: {e}")
            return False
    
    def stop_listener(self) -> bool:
        """
        ホットキーリスナーを停止する
        
        Returns
        -------
        bool
            リスナー停止の成功・失敗
        """
        if self.listener:
            try:
                self.listener.stop()
                self.listener = None
                return True
            except Exception as e:
                print(f"Failed to stop hotkey listener: {e}")
        
        return False
    
    def clear_all_hotkeys(self) -> bool:
        """
        すべてのホットキー登録を解除する
        
        Returns
        -------
        bool
            解除の成功・失敗
        """
        self.stop_listener()
        self.hotkeys.clear()
        return True
    
    @staticmethod
    def parse_hotkey_string(hotkey_str: str) -> Optional[str]:
        """
        ホットキー文字列をpynput形式に変換
        
        Parameters
        ----------
        hotkey_str : str
            'ctrl+shift+r'のような形式のホットキー文字列
            
        Returns
        -------
        Optional[str]
            pynput形式のホットキー文字列（例: '<ctrl>+<shift>+r'）
            無効な入力の場合はNone
        """
        if not hotkey_str:
            return None
            
        # 大文字小文字を正規化
        hotkey_str = hotkey_str.lower()
        
        # 修飾キーのマッピング
        modifier_mapping = {
            'ctrl': '<ctrl>',
            'control': '<ctrl>',
            'alt': '<alt>',
            'option': '<alt>',  # macOS用
            'shift': '<shift>',
            'cmd': '<cmd>',
            'command': '<cmd>',
            'win': '<cmd>',
            'windows': '<cmd>',
            'meta': '<cmd>'
        }
        
        # 特殊キーのマッピング
        special_key_mapping = {
            'f1': '<f1>', 'f2': '<f2>', 'f3': '<f3>', 'f4': '<f4>',
            'f5': '<f5>', 'f6': '<f6>', 'f7': '<f7>', 'f8': '<f8>',
            'f9': '<f9>', 'f10': '<f10>', 'f11': '<f11>', 'f12': '<f12>',
            'esc': '<esc>', 'escape': '<esc>',
            'tab': '<tab>',
            'space': '<space>',
            'backspace': '<backspace>', 'bs': '<backspace>',
            'enter': '<enter>', 'return': '<enter>',
            'ins': '<insert>', 'insert': '<insert>',
            'del': '<delete>', 'delete': '<delete>',
            'home': '<home>',
            'end': '<end>',
            'pageup': '<page_up>', 'pgup': '<page_up>',
            'pagedown': '<page_down>', 'pgdn': '<page_down>',
            'up': '<up>', 'down': '<down>', 'left': '<left>', 'right': '<right>',
            'capslock': '<caps_lock>', 'caps': '<caps_lock>',
            'numlock': '<num_lock>', 'num': '<num_lock>',
            'scrolllock': '<scroll_lock>', 'scrl': '<scroll_lock>',
            'prtsc': '<print_screen>', 'printscreen': '<print_screen>'
        }
        
        parts = hotkey_str.split('+')
        processed_parts = []
        
        # 少なくとも1つのキーが必要
        if not parts:
            return None
            
        for part in parts:
            part = part.strip()
            if part in modifier_mapping:
                processed_parts.append(modifier_mapping[part])
            elif part in special_key_mapping:
                processed_parts.append(special_key_mapping[part])
            elif len(part) == 1:  # 単一文字（a-z, 0-9など）
                processed_parts.append(part)
            else:
                print(f"Warning: Unknown key '{part}' in hotkey. Using as is.")
                processed_parts.append(part)
        
        # 最低1つのキーが存在することを確認
        if not processed_parts:
            return None
            
        return '+'.join(processed_parts)
    
    @staticmethod
    def is_valid_hotkey(hotkey_str: str) -> bool:
        """
        ホットキー文字列が有効かどうか検証する
        
        Parameters
        ----------
        hotkey_str : str
            検証するホットキー文字列
            
        Returns
        -------
        bool
            ホットキーが有効かどうか
        """
        return HotkeyManager.parse_hotkey_string(hotkey_str) is not None
    
    @staticmethod
    def contains_modifier(hotkey_str: str) -> bool:
        """
        ホットキーに修飾キーが含まれているかを確認する
        
        Parameters
        ----------
        hotkey_str : str
            確認するホットキー文字列
            
        Returns
        -------
        bool
            修飾キーが含まれているかどうか
        """
        if not hotkey_str:
            return False
            
        hotkey_str = hotkey_str.lower()
        parts = hotkey_str.split('+')
        
        modifiers = ['ctrl', 'control', 'alt', 'shift', 'cmd', 'command', 'win', 'windows', 'meta']
        return any(part in modifiers for part in parts) 