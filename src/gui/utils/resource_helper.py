import os
import sys
from pathlib import Path

def getResourcePath(relative_path):
    """
    PyInstallerでバンドルされている場合や通常実行時のリソースパスを解決する
    
    Parameters
    ----------
    relative_path : str
        取得したいリソースの相対パス
        
    Returns
    -------
    str
        解決された絶対パス
    """
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
            # src/gui/utils/resource_helper.py から4階層上に移動してルートを取得
            current_file = os.path.abspath(__file__)
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        
        return os.path.join(base_path, relative_path)
    except Exception as e:
        print(f"Resource path resolution error: {e}")
        return relative_path 