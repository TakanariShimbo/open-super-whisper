"""
語彙とシステム指示のペア管理モジュール

カスタム語彙とシステム指示のペアを管理するためのクラスを提供します。
ユーザーが保存した複数のペアセットを管理し、それらを選択して利用できるようにします。
"""

from typing import Dict, List, Optional

# 内部定数
_DEFAULT_INSTRUCTION_SET_NAME = "デフォルト"
_INSTRUCTION_SETS_SETTINGS_PREFIX = "InstructionSets"

class InstructionSet:
    """
    カスタム語彙とシステム指示のペアを表すクラス
    
    名前付きの語彙リストとシステム指示リストのペアを管理します。
    """
    
    def __init__(self, name: str, vocabulary: List[str] = None, instructions: List[str] = None):
        """
        InstructionSetの初期化
        
        Parameters
        ----------
        name : str
            このセットの名前
        vocabulary : List[str], optional
            カスタム語彙のリスト
        instructions : List[str], optional
            システム指示のリスト
        """
        self.name = name
        self.vocabulary = vocabulary or []
        self.instructions = instructions or []
    
    def to_dict(self) -> Dict:
        """
        このセットを辞書形式に変換
        
        Returns
        -------
        Dict
            セットの内容を表す辞書
        """
        return {
            "name": self.name,
            "vocabulary": self.vocabulary,
            "instructions": self.instructions
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'InstructionSet':
        """
        辞書からInstructionSetオブジェクトを作成
        
        Parameters
        ----------
        data : Dict
            セットの内容を表す辞書
        
        Returns
        -------
        InstructionSet
            作成されたInstructionSetオブジェクト
        """
        return cls(
            name=data.get("name", "無名セット"),
            vocabulary=data.get("vocabulary", []),
            instructions=data.get("instructions", [])
        )


class InstructionSetManager:
    """
    複数のInstructionSetを管理するクラス
    
    QSettingsオブジェクトからのロード、保存、セットの追加・削除・選択など
    指示セットの作成、管理、アクティブ化を行います。
    
    Note
    ----
    このクラスは設定の保存と読み込みにQSettingsオブジェクトを使用します。
    外部からsettingsオブジェクトを渡す必要があります。
    """
    
    def __init__(self, settings=None):
        """
        InstructionSetManagerの初期化
        
        Parameters
        ----------
        settings : QSettings, optional
            設定オブジェクト
        """
        self.sets: List[InstructionSet] = []
        self.active_set: Optional[InstructionSet] = None
        self.settings = settings
        
        # デフォルトのセットを追加
        default_set = InstructionSet(_DEFAULT_INSTRUCTION_SET_NAME, [], [])
        self.add_set(default_set)
        self.set_active(0)  # 最初のセットをアクティブに
    
    def add_set(self, instruction_set: InstructionSet) -> int:
        """
        新しいセットを追加
        
        Parameters
        ----------
        instruction_set : InstructionSet
            追加するセット
        
        Returns
        -------
        int
            追加されたセットのインデックス
        """
        self.sets.append(instruction_set)
        return len(self.sets) - 1
    
    def remove_set(self, index: int) -> bool:
        """
        指定されたインデックスのセットを削除
        
        Parameters
        ----------
        index : int
            削除するセットのインデックス
        
        Returns
        -------
        bool
            削除が成功したかどうか
        """
        if 0 <= index < len(self.sets):
            # アクティブセットを削除する場合は、アクティブセットを変更
            if self.active_set == self.sets[index]:
                self.active_set = self.sets[0] if len(self.sets) > 1 else None
                
            del self.sets[index]
            return True
        return False
    
    def set_active(self, index: int) -> bool:
        """
        指定されたインデックスのセットをアクティブに設定
        
        Parameters
        ----------
        index : int
            アクティブにするセットのインデックス
        
        Returns
        -------
        bool
            設定が成功したかどうか
        """
        if 0 <= index < len(self.sets):
            self.active_set = self.sets[index]
            return True
        return False
    
    def get_active_vocabulary(self) -> List[str]:
        """
        現在アクティブなセットの語彙リストを取得
        
        Returns
        -------
        List[str]
            語彙リスト
        """
        if self.active_set:
            return self.active_set.vocabulary
        return []
    
    def get_active_instructions(self) -> List[str]:
        """
        現在アクティブなセットの指示リストを取得
        
        Returns
        -------
        List[str]
            指示リスト
        """
        if self.active_set:
            return self.active_set.instructions
        return []
    
    def save_to_settings(self) -> bool:
        """
        セットの一覧を設定に保存
        
        Returns
        -------
        bool
            保存が成功したかどうか
        """
        if not self.settings:
            return False
        
        try:
            # アクティブセットのインデックスを見つける
            active_index = -1
            for i, s in enumerate(self.sets):
                if s == self.active_set:
                    active_index = i
                    break
            
            # セットの数を保存
            prefix = _INSTRUCTION_SETS_SETTINGS_PREFIX
            self.settings.setValue(f"{prefix}/Count", len(self.sets))
            self.settings.setValue(f"{prefix}/ActiveIndex", active_index)
            
            # 各セットを保存
            for i, set_obj in enumerate(self.sets):
                set_prefix = f"{prefix}/Set{i}/"
                self.settings.setValue(f"{set_prefix}Name", set_obj.name)
                
                # 語彙を保存
                self.settings.setValue(f"{set_prefix}VocabularyCount", len(set_obj.vocabulary))
                for j, vocab in enumerate(set_obj.vocabulary):
                    self.settings.setValue(f"{set_prefix}Vocabulary{j}", vocab)
                
                # 指示を保存
                self.settings.setValue(f"{set_prefix}InstructionsCount", len(set_obj.instructions))
                for j, instr in enumerate(set_obj.instructions):
                    self.settings.setValue(f"{set_prefix}Instruction{j}", instr)
            
            self.settings.sync()
            return True
        except Exception as e:
            print(f"設定保存エラー: {e}")
            return False
    
    def load_from_settings(self) -> bool:
        """
        設定からセットの一覧を読み込み
        
        Returns
        -------
        bool
            読み込みが成功したかどうか
        """
        if not self.settings:
            return False
        
        try:
            # 既存のセットをクリア
            self.sets = []
            
            # セットの数を取得
            prefix = _INSTRUCTION_SETS_SETTINGS_PREFIX
            count = self.settings.value(f"{prefix}/Count", 0, type=int)
            active_index = self.settings.value(f"{prefix}/ActiveIndex", -1, type=int)
            
            # セットが保存されていない場合はデフォルトを作成
            if count <= 0:
                default_set = InstructionSet(_DEFAULT_INSTRUCTION_SET_NAME, [], [])
                self.add_set(default_set)
                self.active_set = default_set
                return True
            
            # 各セットを読み込み
            for i in range(count):
                set_prefix = f"{prefix}/Set{i}/"
                name = self.settings.value(f"{set_prefix}Name", f"セット {i+1}", type=str)
                
                # 語彙を読み込み
                vocab_count = self.settings.value(f"{set_prefix}VocabularyCount", 0, type=int)
                vocabulary = []
                for j in range(vocab_count):
                    vocab = self.settings.value(f"{set_prefix}Vocabulary{j}", "", type=str)
                    if vocab:
                        vocabulary.append(vocab)
                
                # 指示を読み込み
                instr_count = self.settings.value(f"{set_prefix}InstructionsCount", 0, type=int)
                instructions = []
                for j in range(instr_count):
                    instr = self.settings.value(f"{set_prefix}Instruction{j}", "", type=str)
                    if instr:
                        instructions.append(instr)
                
                # セットを作成して追加
                set_obj = InstructionSet(name, vocabulary, instructions)
                self.add_set(set_obj)
            
            # アクティブセットを設定
            if 0 <= active_index < len(self.sets):
                self.active_set = self.sets[active_index]
            elif self.sets:
                self.active_set = self.sets[0]
            
            return True
        except Exception as e:
            print(f"設定読み込みエラー: {e}")
            # エラー時はデフォルトのセットを作成
            self.sets = []
            default_set = InstructionSet(_DEFAULT_INSTRUCTION_SET_NAME, [], [])
            self.add_set(default_set)
            self.active_set = default_set
            return False 