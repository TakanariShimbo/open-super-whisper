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
    Class to handle audio recording functionality
    """
    
    def __init__(self, sample_rate=16000, channels=1):
        """
        Initialize the audio recorder
        
        Parameters:
        -----------
        sample_rate : int
            The sample rate to record audio at (default: 16000)
        channels : int
            The number of audio channels (default: 1 for mono)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False
        self.audio_data = []
        self.temp_dir = tempfile.gettempdir()
        self._record_thread = None

    def start_recording(self):
        """Start recording audio"""
        self.recording = True
        self.audio_data = []
        
        # Start recording in a separate thread
        self._record_thread = threading.Thread(target=self._record)
        self._record_thread.daemon = True
        self._record_thread.start()
        
        return True
    
    def stop_recording(self):
        """Stop recording audio and return the filename of the saved audio"""
        if not self.recording:
            return None
            
        self.recording = False
        
        # Wait for recording thread to finish
        if self._record_thread and self._record_thread.is_alive():
            self._record_thread.join()
        
        # Generate a filename based on current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.temp_dir, f"recording_{timestamp}.wav")
        
        # Save the recorded audio
        if len(self.audio_data) > 0:
            audio_data = np.concatenate(self.audio_data, axis=0)
            sf.write(filename, audio_data, self.sample_rate)
            return filename
        
        return None
    
    def _record(self):
        """Internal method to record audio data"""
        try:
            def callback(indata, frames, time, status):
                if status:
                    print(f"Status: {status}")
                if self.recording:
                    self.audio_data.append(indata.copy())
            
            with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=callback):
                while self.recording:
                    sd.sleep(100)  # Sleep to avoid consuming too much CPU
                    
        except Exception as e:
            print(f"Error recording: {e}")
            self.recording = False

    def is_recording(self):
        """Check if recording is in progress"""
        return self.recording
