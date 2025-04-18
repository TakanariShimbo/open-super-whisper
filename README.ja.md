# Open Super Whisper

OpenAIのWhisperモデルを使用した音声文字起こしのためのPythonデスクトップアプリケーション。

## 特徴

- 🎙️ マイクから直接音声を録音
- 📁 音声ファイルのインポート（MP3、WAV、M4A、OGG、FLACをサポート）
- 🌎 自動言語検出機能付きで100以上の言語をサポート
- 📝 文字起こし精度を向上させるカスタム語彙機能
- 📋 クリップボードに文字起こし内容をコピー
- 💾 テキストファイルとして保存
- 🔄 リアルタイムの録音状態表示とタイマー

## 必要条件

- Python 3.8以上
- OpenAI APIキー
- Windowsオペレーティングシステム

## インストール方法

### UV を使用した方法（高速）

[UV](https://github.com/astral-sh/uv)は高速で効率的なPythonパッケージインストーラーおよび環境マネージャーです。従来のpipやvenvよりも高速で、依存関係の解決も優れています。

1. UVがインストールされているか確認：

```bash
uv --version
```

2. インストールされていない場合は、次のコマンドでインストールできます：

```bash
# pipを使用する場合
pip install uv

# または公式の方法
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. リポジトリをクローンまたはダウンロード

4. UVのsyncコマンドを使用してプロジェクトをセットアップ（仮想環境の作成と依存関係のインストールを自動的に行います）：

```bash
uv sync
```

5. 仮想環境をアクティベート：

```bash
# Windows（コマンドプロンプトの場合）
.venv\Scripts\activate.bat
# または Windows（PowerShellの場合）
# .\.venv\Scripts\activate.ps1
```

> **注意**: PowerShellで`activate.ps1`実行時に「このシステムではスクリプトの実行が無効になっている」というエラーが表示される場合は、以下のいずれかの方法を試してください：
> 
> 1. コマンドプロンプト（cmd.exe）を使用して`.venv\Scripts\activate.bat`を実行
> 2. PowerShellで以下のコマンドを実行して、現在のセッションのみ実行ポリシーを変更:
>    ```powershell
>    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
>    ```
>    その後、`.\.venv\Scripts\activate.ps1`を実行
> 3. 管理者権限でPowerShellを実行し、システム全体の実行ポリシーを変更（セキュリティ上のリスクを理解した上で行ってください）:
>    ```powershell
>    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
>    ```

6. アプリケーションを実行：

```bash
python main.py
```

## 使用方法

### APIキーの設定

1. 初回起動時にOpenAI APIキーの入力が求められます
2. APIキーをお持ちでない場合は、[OpenAIのウェブサイト](https://platform.openai.com/api-keys)から取得できます
3. APIキーは今後の使用のために保存されます

### 音声の録音

1. 「録音開始」ボタンをクリックしてマイクからの録音を開始
2. 「録音停止」をクリックして録音を終了
3. アプリケーションは自動的に録音内容を文字起こしします

### 音声ファイルのインポート

1. 「音声ファイル読込」ボタンをクリック
2. コンピューターから音声ファイルを選択
3. アプリケーションがファイルを処理して文字起こしします

### 言語選択

1. 録音やファイルのインポート前に、ドロップダウンメニューから言語を選択
2. 「自動検出」を選択すると、Whisperが自動的に言語を識別します

### カスタム語彙

1. ツールバーの「カスタム語彙」をクリック
2. 音声に含まれる可能性のある特定の用語、名前、フレーズを追加
3. これらの用語は文字起こしの精度向上に役立ちます

### 文字起こし結果の管理

1. メインテキストエリアで文字起こし結果を表示
2. 必要に応じてテキストを編集（テキストエリアは編集可能）
3. ツールバーのボタンを使用して：
   - クリップボードに文字起こしをコピー
   - テキストファイルとして保存

## ライセンス

このプロジェクトはMITライセンスの下で公開されています - 詳細はLICENSEファイルをご覧ください。

## 謝辞

- このアプリケーションは[OpenAIのWhisper API](https://platform.openai.com/docs/guides/speech-to-text)を音声認識に使用しています
- ユーザーインターフェースは[PyQt6](https://www.riverbankcomputing.com/software/pyqt/)で構築されています
- [Super Whisper](https://superwhisper.com/)デスクトップアプリケーションに触発されています
