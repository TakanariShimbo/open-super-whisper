"""
アプリケーションのUIテキストラベルを定義するモジュール

このモジュールには、アプリケーション全体で使用されるUIテキストが含まれています。
テキストの一元管理により、多言語対応や表現の統一が容易になります。
"""

class AppLabels:
    """アプリケーション全体のUIテキストを管理するクラス"""
    
    # アプリケーション基本情報
    APP_TITLE = "Open Super Whisper"
    
    # メインウィンドウ
    RECORD_START_BUTTON = "録音開始"
    RECORD_STOP_BUTTON = "録音停止"
    LANGUAGE_LABEL = "言語:"
    MODEL_LABEL = "モデル:"
    AUTO_DETECT = "自動検出"
    TRANSCRIPTION_TITLE = "文字起こし結果"
    TRANSCRIPTION_PLACEHOLDER = "ここに文字起こしが表示されます..."
    STATUS_READY = "準備完了"
    
    # ツールバーアイテム
    API_KEY_SETTINGS = "APIキー設定"
    CUSTOM_VOCABULARY = "カスタム語彙"
    SYSTEM_INSTRUCTIONS = "システム指示"
    COPY_TO_CLIPBOARD = "クリップボードにコピー"
    HOTKEY_SETTINGS = "ホットキー設定"
    AUTO_COPY = "自動コピー"
    SOUND_NOTIFICATION = "通知音"
    STATUS_INDICATOR = "状態インジケータ"
    EXIT_APP = "アプリケーション終了"
    
    # ステータスメッセージ
    STATUS_RECORDING = "録音中..."
    STATUS_TRANSCRIBING = "文字起こし中..."
    STATUS_TRANSCRIBED = "文字起こしが完了しました"
    STATUS_TRANSCRIBED_COPIED = "文字起こしが完了し、クリップボードにコピーしました"
    STATUS_COPIED = "クリップボードにコピーしました"
    STATUS_API_KEY_SAVED = "APIキーが保存されました"
    STATUS_HOTKEY_SET = "ホットキーを {0} に設定しました"
    STATUS_AUTO_COPY_ENABLED = "自動コピーを有効にしました"
    STATUS_AUTO_COPY_DISABLED = "自動コピーを無効にしました"
    STATUS_SOUND_ENABLED = "通知音を有効にしました"
    STATUS_SOUND_DISABLED = "通知音を無効にしました"
    STATUS_INDICATOR_SHOWN = "状態インジケータを表示にしました"
    STATUS_INDICATOR_HIDDEN = "状態インジケータを非表示にしました"
    STATUS_VOCABULARY_ADDED = "{0}個の語彙を追加しました"
    STATUS_INSTRUCTIONS_SET = "{0}個のシステム指示を設定しました"
    STATUS_MODEL_CHANGED = "文字起こしモデルを「{0}」に変更しました"
    
    # APIキーダイアログ
    API_KEY_DIALOG_TITLE = "OpenAI APIキー"
    API_KEY_LABEL = "APIキー:"
    API_KEY_INFO = "このアプリケーションを使用するにはOpenAI APIキーが必要です。お持ちでない場合は、https://platform.openai.com/api-keys から取得できます。"
    SAVE_BUTTON = "保存"
    CANCEL_BUTTON = "キャンセル"
    
    # カスタム語彙ダイアログ
    VOCABULARY_DIALOG_TITLE = "カスタム語彙"
    VOCABULARY_SECTION_TITLE = "カスタム語彙の単語"
    VOCABULARY_PLACEHOLDER = "新しい単語を入力..."
    ADD_BUTTON = "追加"
    REMOVE_SELECTED = "選択項目を削除"
    REMOVE_ALL = "すべて削除"
    OK_BUTTON = "OK"
    
    # システム指示ダイアログ
    INSTRUCTIONS_DIALOG_TITLE = "システム指示"
    INSTRUCTIONS_INFO = "ここで文字起こしのための特別な指示を設定できます。例：\n" \
                      "- \"えー、あの、などのフィラーを無視してください\"\n" \
                      "- \"句読点を適切に入れてください\"\n" \
                      "- \"段落に分けてください\""
    INSTRUCTIONS_SECTION_TITLE = "システム指示リスト:"
    INSTRUCTIONS_PLACEHOLDER = "新しい指示を入力..."
    
    # グローバルホットキーダイアログ
    HOTKEY_DIALOG_TITLE = "グローバルホットキー設定"
    HOTKEY_LABEL = "ホットキー:"
    HOTKEY_PLACEHOLDER = "例: ctrl+shift+r"
    HOTKEY_INFO = "録音を開始/停止するグローバルホットキーを設定します。例: ctrl+shift+r, alt+w など"
    
    # ホットキー情報ダイアログ
    HOTKEY_INFO_TITLE = "ホットキー情報"
    HOTKEY_INFO_MESSAGE = "Open Super Whisperは常にバックグラウンドで実行されています。\n" \
                        "グローバルホットキー: {0} で録音を開始/停止できます。\n" \
                        "この設定はツールバーの「ホットキー設定」から変更できます。"
    
    # 状態インジケーター
    INDICATOR_RECORDING = "録音中"
    INDICATOR_TRANSCRIBING = "文字起こし中"
    INDICATOR_COPIED = "コピー完了"
    
    # システムトレイメニュー
    TRAY_SHOW = "表示"
    TRAY_RECORD = "録音開始/停止"
    TRAY_EXIT = "終了"
    
    # エラーメッセージ
    ERROR_TITLE = "エラー"
    ERROR_API_KEY_REQUIRED = "先にAPIキーを設定してください"
    ERROR_SYSTEM_TRAY = "システムトレイがサポートされていません。"
    ERROR_HOTKEY = "ホットキー設定エラー: {0}"
    
    # 情報メッセージ
    INFO_TITLE = "情報"
    INFO_TRAY_MINIMIZED = "アプリケーションはシステムトレイで実行されています。\n" \
                        "完全に終了するには、トレイアイコンから「終了」を選択するか、\n" \
                        "ツールバーの「アプリケーション終了」をクリックしてください。"
    
    # 言語名
    LANGUAGE_ENGLISH = "英語"
    LANGUAGE_SPANISH = "スペイン語"
    LANGUAGE_FRENCH = "フランス語"
    LANGUAGE_GERMAN = "ドイツ語"
    LANGUAGE_ITALIAN = "イタリア語"
    LANGUAGE_PORTUGUESE = "ポルトガル語"
    LANGUAGE_JAPANESE = "日本語"
    LANGUAGE_KOREAN = "韓国語"
    LANGUAGE_CHINESE = "中国語"
    LANGUAGE_RUSSIAN = "ロシア語" 