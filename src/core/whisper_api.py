import os
import json
import tempfile
from pathlib import Path
import openai
from dotenv import load_dotenv

# Load environment variables from a .env file if available
load_dotenv()


class WhisperTranscriber:
    """
    Class to handle transcription using the OpenAI Whisper API
    """
    
    # 利用可能なモデルのリスト
    AVAILABLE_MODELS = [
        {"id": "whisper-1", "name": "Whisper (オリジナル)", "description": "OpenAIのオープンソースWhisperモデル"},
        {"id": "gpt-4o-transcribe", "name": "GPT-4o Transcribe", "description": "高性能な文字起こしモデル"},
        {"id": "gpt-4o-mini-transcribe", "name": "GPT-4o Mini Transcribe", "description": "軽量で高速な文字起こしモデル"}
    ]
    
    def __init__(self, api_key=None):
        """
        Initialize the Whisper transcriber
        
        Parameters:
        -----------
        api_key : str, optional
            OpenAI API key. If not provided, it will try to get it from OPENAI_API_KEY env variable.
        """
        # Use provided API key or get from environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI APIキーが必要です。直接提供するか、OPENAI_API_KEY環境変数を設定してください。")
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Set default parameters
        self.model = "whisper-1"  # The Whisper model to use
        
        # Cache for custom vocabulary (prompt)
        self.custom_vocabulary = []
        
        # システム指示用のリスト
        self.system_instructions = []
    
    @classmethod
    def get_available_models(cls):
        """利用可能なモデルのリストを返す"""
        return cls.AVAILABLE_MODELS
        
    def set_model(self, model):
        """Set the model to use for transcription"""
        self.model = model
        
    def add_custom_vocabulary(self, terms):
        """Add custom vocabulary terms to improve transcription accuracy"""
        if isinstance(terms, str):
            terms = [terms]
        self.custom_vocabulary.extend(terms)
    
    def clear_custom_vocabulary(self):
        """Clear the custom vocabulary list"""
        self.custom_vocabulary = []
    
    def get_custom_vocabulary(self):
        """Get the current custom vocabulary list"""
        return self.custom_vocabulary
    
    def add_system_instruction(self, instructions):
        """システムプロンプトに指示を追加"""
        if isinstance(instructions, str):
            instructions = [instructions]
        self.system_instructions.extend(instructions)
    
    def clear_system_instructions(self):
        """システムプロンプトをクリア"""
        self.system_instructions = []
    
    def get_system_instructions(self):
        """現在のシステムプロンプトを取得"""
        return self.system_instructions
    
    def _build_prompt(self):
        """語彙とシステム指示を含むプロンプトを構築"""
        prompt_parts = []
        
        # カスタム語彙を追加
        if self.custom_vocabulary:
            prompt_parts.append("Vocabulary: " + ", ".join(self.custom_vocabulary))
        
        # システム指示を追加
        if self.system_instructions:
            prompt_parts.append("Instructions: " + ". ".join(self.system_instructions))
        
        if not prompt_parts:
            return None
            
        return " ".join(prompt_parts)
        
    def transcribe(self, audio_file, language=None, response_format="text"):
        """
        Transcribe audio using the OpenAI Whisper API
        
        Parameters:
        -----------
        audio_file : str
            Path to the audio file to transcribe
        language : str, optional
            The language code (e.g., "en", "ja", "zh") for transcription
        response_format : str, optional
            Format for the response: "text", "json", "verbose_json", or "vtt"
            
        Returns:
        --------
        str or dict
            Transcription result as string or dict depending on response_format
        """
        try:
            # Check if file exists
            audio_path = Path(audio_file)
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_file}")
            
            # Build parameters for the API call
            params = {
                "model": self.model,
                "response_format": response_format,
            }
            
            # Add language if specified
            if language:
                params["language"] = language
                
            # Add prompt with custom vocabulary if available
            prompt = self._build_prompt()
            if prompt:
                params["prompt"] = prompt
            
            # Open the audio file for the API call
            with open(audio_path, "rb") as audio:
                # Call the OpenAI API
                response = self.client.audio.transcriptions.create(
                    file=audio,
                    **params
                )
                
            # Process the response based on the requested format
            if response_format == "json" or response_format == "verbose_json":
                # For JSON response formats, parse the response text
                return json.loads(response)
            else:
                # For text, srt, or vtt, just return the string
                return str(response)
                
        except Exception as e:
            print(f"Error during transcription: {e}")
            return f"Error: {str(e)}"
