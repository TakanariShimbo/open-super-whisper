import os
import json
import tempfile
from pathlib import Path
import openai


class WhisperTranscriber:
    """
    OpenAI Whisper APIを使用した文字起こし処理を行うクラス
    
    APIを使って音声ファイルのテキスト変換を行い、カスタム語彙やシステム指示を
    活用して精度を向上させる機能を提供します。
    """
    
    # 利用可能なモデルのリスト
    AVAILABLE_MODELS = [
        {"id": "whisper-1", "name": "Whisper", "description": "OpenAI's open-source Whisper model"},
        {"id": "gpt-4o-transcribe", "name": "GPT-4o Transcribe", "description": "High-performance transcription model"},
        {"id": "gpt-4o-mini-transcribe", "name": "GPT-4o Mini Transcribe", "description": "Lightweight and fast transcription model"}
    ]
    
    def __init__(self, api_key=None):
        """
        Whisper文字起こしクラスの初期化
        
        Parameters
        ----------
        api_key : str, optional
            OpenAI APIキー。提供されない場合はOPENAI_API_KEY環境変数から取得を試みます。
        """
        # 提供されたAPIキーを使用するか、環境から取得
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Please provide it directly or set the OPENAI_API_KEY environment variable.")
        
        # OpenAIクライアントの初期化
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # デフォルトパラメータの設定
        self.model = "whisper-1"  # 使用するWhisperモデル
        
        # カスタム語彙（プロンプト）のキャッシュ
        self.custom_vocabulary = []
        
        # システム指示用のリスト
        self.system_instructions = []
    
    @classmethod
    def get_available_models(cls):
        """
        利用可能なモデルのリストを返す
        
        Returns
        -------
        list
            利用可能なモデルの情報を含む辞書のリスト
        """
        return cls.AVAILABLE_MODELS
        
    def set_model(self, model):
        """
        文字起こしに使用するモデルを設定する
        
        Parameters
        ----------
        model : str
            使用するモデルのID
        """
        self.model = model
        
    def add_custom_vocabulary(self, terms):
        """
        文字起こし精度向上のためのカスタム語彙を追加する
        
        Parameters
        ----------
        terms : str or list
            追加する語彙（単語または単語のリスト）
        """
        if isinstance(terms, str):
            terms = [terms]
        self.custom_vocabulary.extend(terms)
    
    def clear_custom_vocabulary(self):
        """
        カスタム語彙リストをクリアする
        """
        self.custom_vocabulary = []
    
    def get_custom_vocabulary(self):
        """
        現在のカスタム語彙リストを取得する
        
        Returns
        -------
        list
            現在設定されているカスタム語彙のリスト
        """
        return self.custom_vocabulary
    
    def add_system_instruction(self, instructions):
        """
        システムプロンプトに指示を追加する
        
        Parameters
        ----------
        instructions : str or list
            追加するシステム指示（文字列または文字列のリスト）
        """
        if isinstance(instructions, str):
            instructions = [instructions]
        self.system_instructions.extend(instructions)
    
    def clear_system_instructions(self):
        """
        システムプロンプトをクリアする
        """
        self.system_instructions = []
    
    def get_system_instructions(self):
        """
        現在のシステムプロンプトを取得する
        
        Returns
        -------
        list
            現在設定されているシステム指示のリスト
        """
        return self.system_instructions
    
    def _build_prompt(self):
        """
        語彙とシステム指示を含むプロンプトを構築する
        
        Returns
        -------
        str or None
            構築されたプロンプト、または指示がない場合はNone
        """
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
        OpenAI Whisper APIを使用して音声を文字起こしする
        
        Parameters
        ----------
        audio_file : str
            文字起こしする音声ファイルのパス
        language : str, optional
            文字起こしの言語コード（例："en"、"ja"、"zh"）
        response_format : str, optional
            応答フォーマット："text"、"json"、"verbose_json"、または"vtt"
            
        Returns
        -------
        str or dict
            応答フォーマットによって文字列または辞書形式の文字起こし結果
        """
        try:
            # ファイルの存在確認
            audio_path = Path(audio_file)
            if not audio_path.exists():
                raise FileNotFoundError(f"音声ファイルが見つかりません: {audio_file}")
            
            # API呼び出し用のパラメータを構築
            params = {
                "model": self.model,
                "response_format": response_format,
            }
            
            # 言語が指定されている場合は追加
            if language:
                params["language"] = language
                
            # カスタム語彙がある場合はプロンプトを追加
            prompt = self._build_prompt()
            if prompt:
                params["prompt"] = prompt
            
            # API呼び出し用に音声ファイルを開く
            with open(audio_path, "rb") as audio:
                # OpenAI APIを呼び出す
                response = self.client.audio.transcriptions.create(
                    file=audio,
                    **params
                )
                
            # 要求されたフォーマットに基づいてレスポンスを処理
            if response_format == "json" or response_format == "verbose_json":
                # JSONレスポンスフォーマットの場合、レスポンステキストを解析
                return json.loads(response)
            else:
                # テキスト、srt、vttの場合は文字列を返す
                return str(response)
                
        except Exception as e:
            print(f"Error occurred during transcription: {e}")
            return f"Error: {str(e)}"
