import os
import time
import wave
import threading
import tempfile
import numpy as np
import sounddevice as sd
import soundfile as sf
from datetime import datetime


class AudioRecorder:
    """
    音声録音機能を処理するクラス
    
    オーディオの録音、保存、状態管理の機能を提供します。
    """
    
    def __init__(self, sample_rate=16000, channels=1):
        """
        AudioRecorderの初期化
        
        Parameters
        ----------
        sample_rate : int
            録音するサンプルレート (デフォルト: 16000)
        channels : int
            オーディオチャンネル数 (デフォルト: 1 モノラル)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False
        self.audio_data = []
        self.temp_dir = tempfile.gettempdir()
        self._record_thread = None

    def start_recording(self):
        """
        音声録音を開始する
        
        Returns
        -------
        bool
            録音開始成功時にTrue
        """
        self.recording = True
        self.audio_data = []
        
        # 別スレッドで録音を開始
        self._record_thread = threading.Thread(target=self._record)
        self._record_thread.daemon = True
        self._record_thread.start()
        
        return True
    
    def stop_recording(self):
        """
        音声録音を停止し、保存したファイル名を返す
        
        Returns
        -------
        str or None
            保存された音声ファイルパス、失敗時はNone
        """
        if not self.recording:
            return None
            
        self.recording = False
        
        # 録音スレッドの終了を待機
        if self._record_thread and self._record_thread.is_alive():
            self._record_thread.join()
        
        # 現在のタイムスタンプに基づいたファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.temp_dir, f"recording_{timestamp}.wav")
        
        # 録音した音声を保存
        if len(self.audio_data) > 0:
            audio_data = np.concatenate(self.audio_data, axis=0)
            sf.write(filename, audio_data, self.sample_rate)
            return filename
        
        return None
    
    def _record(self):
        """
        音声データを録音する内部メソッド
        """
        try:
            def callback(indata, frames, time, status):
                if status:
                    print(f"Status: {status}")
                if self.recording:
                    self.audio_data.append(indata.copy())
            
            with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=callback):
                while self.recording:
                    sd.sleep(100)  # CPUの過剰消費を避けるためのスリープ
                    
        except Exception as e:
            print(f"Recording error: {e}")
            self.recording = False

    def is_recording(self):
        """
        録音中かどうかをチェック
        
        Returns
        -------
        bool
            録音中の場合True
        """
        return self.recording
