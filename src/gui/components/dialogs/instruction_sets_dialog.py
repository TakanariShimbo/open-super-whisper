import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QLineEdit, QMessageBox,
    QTextEdit, QWidget, QInputDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QFrame, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QColor, QFont, QIcon, QPixmap
from PyQt6.QtCore import QSize

from src.core.instruction_sets import InstructionSet, InstructionSetManager
from src.gui.resources.config import AppConfig
from src.gui.resources.labels import AppLabels
from src.gui.resources.styles import AppStyles, AppTheme
from src.gui.utils.resource_helper import getResourcePath
from src.gui.components.dialogs.simple_input_dialog import SimpleInputDialog
from src.gui.components.dialogs.simple_message_dialog import SimpleMessageDialog

class InstructionSetsDialog(QDialog):
    """
    語彙とシステム指示のペアセットを管理するためのダイアログ
    
    ユーザーがカスタム語彙とシステム指示のペアを複数作成し、
    管理・選択するためのインターフェースを提供します。
    """
    
    # ダイアログの定数
    BUTTON_WIDTH = int(AppTheme.BUTTON_WIDTH_MD.replace("px", ""))
    ACTIVATE_BUTTON_WIDTH = 180
    ICON_SIZE = int(AppTheme.ICON_SIZE_MD.replace("px", ""))
    TABLE_ROW_HEIGHT = 36
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(AppLabels.INSTRUCTION_SETS_DIALOG_TITLE)
        # ダイアログを縦に長くして、内容が収まるようにサイズを調整
        self.setFixedSize(AppTheme.MAIN_WINDOW_WIDTH, int(AppTheme.MAIN_WINDOW_HEIGHT * 1.2))
        
        # ダイアログスタイル設定 - 新しいスタイル適用方法
        self.setStyleSheet(AppStyles.get_dialog_style())
        
        # アイコンの設定
        icon_path = getResourcePath("assets/icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 設定の読み込み
        self.settings = QSettings(AppConfig.APP_ORGANIZATION, AppConfig.APP_NAME)
        
        # InstructionSetManagerの初期化（QSettingsを使用）
        self.manager = InstructionSetManager(self.settings)
        self.manager.load_from_settings()
        
        # UI初期化
        self.init_ui()
        
        # テーブルを更新
        self.update_table_view()
    
    def init_ui(self):
        """ダイアログのUIを初期化"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            int(AppTheme.MAIN_MARGIN), 
            int(AppTheme.MAIN_MARGIN), 
            int(AppTheme.MAIN_MARGIN), 
            int(AppTheme.MAIN_MARGIN)
        )
        main_layout.setSpacing(int(AppTheme.MAIN_SPACING))
        
        # ダイアログフレーム
        dialog_frame = QFrame(self)
        dialog_frame.setObjectName("dialogFrame")
        frame_layout = QVBoxLayout(dialog_frame)
        frame_layout.setContentsMargins(int(AppTheme.PADDING_MD.split()[0].replace("px", "")), 
                                      int(AppTheme.PADDING_MD.split()[0].replace("px", "")), 
                                      int(AppTheme.PADDING_MD.split()[0].replace("px", "")), 
                                      int(AppTheme.PADDING_MD.split()[0].replace("px", "")))
        frame_layout.setSpacing(int(AppTheme.SPACING_MD.replace("px", "")))
        
        # ダイアログタイトル
        title_label = QLabel(AppLabels.INSTRUCTION_SETS_DIALOG_TITLE)
        title_label.setObjectName("dialogTitle")
        frame_layout.addWidget(title_label)
        
        # セパレーター
        separator = QFrame()
        separator.setObjectName("separatorLine")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        frame_layout.addWidget(separator)
        
        # 上部: 一覧表示と管理ボタン
        top_section = QWidget()
        top_layout = QVBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(int(AppTheme.SPACING_MD.replace("px", "")))
        
        # タイトルとボタンのレイアウト
        header_layout = QHBoxLayout()
        
        # セクションタイトル
        section_title = QLabel(AppLabels.INSTRUCTION_SETS_TABLE_MODE_TITLE)
        section_title.setObjectName("sectionTitle")
        header_layout.addWidget(section_title)
        
        header_layout.addStretch()
        
        # アクティブ化ボタン
        self.activate_button = QPushButton(AppLabels.INSTRUCTION_SETS_ACTIVATE_BUTTON)
        self.activate_button.setProperty("class", "primary")
        self.activate_button.clicked.connect(self.activate_current_set)
        self.activate_button.setFixedWidth(self.ACTIVATE_BUTTON_WIDTH)
        header_layout.addWidget(self.activate_button)
        
        header_layout.addSpacing(int(AppTheme.SPACING_SM.replace("px", "")))
        
        self.add_set_button = QPushButton(AppLabels.INSTRUCTION_SETS_ADD_BUTTON)
        self.add_set_button.setProperty("class", "primary")
        self.add_set_button.clicked.connect(self.add_new_set)
        self.add_set_button.setFixedWidth(self.BUTTON_WIDTH)
        header_layout.addWidget(self.add_set_button)
        
        header_layout.addSpacing(int(AppTheme.SPACING_SM.replace("px", "")))
        
        self.rename_set_button = QPushButton(AppLabels.INSTRUCTION_SETS_RENAME_BUTTON)
        self.rename_set_button.setProperty("class", "primary")
        self.rename_set_button.clicked.connect(self.rename_selected_set)
        self.rename_set_button.setFixedWidth(self.BUTTON_WIDTH)
        header_layout.addWidget(self.rename_set_button)
        
        header_layout.addSpacing(int(AppTheme.SPACING_SM.replace("px", "")))
        
        self.remove_set_button = QPushButton(AppLabels.INSTRUCTION_SETS_REMOVE_BUTTON)
        self.remove_set_button.setProperty("class", "danger")
        self.remove_set_button.clicked.connect(self.remove_selected_set)
        self.remove_set_button.setFixedWidth(self.BUTTON_WIDTH)
        header_layout.addWidget(self.remove_set_button)
        
        top_layout.addLayout(header_layout)
        
        # 一覧テーブル
        self.sets_table = QTableWidget()
        self.sets_table.setColumnCount(3)
        self.sets_table.setHorizontalHeaderLabels([
            AppLabels.INSTRUCTION_SETS_TABLE_NAME_COLUMN,
            AppLabels.INSTRUCTION_SETS_TABLE_VOCABULARY_COLUMN,
            AppLabels.INSTRUCTION_SETS_TABLE_INSTRUCTIONS_COLUMN
        ])
        
        # 列
        self.sets_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.sets_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.sets_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        # テーブルの設定
        self.sets_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sets_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.sets_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.sets_table.setAlternatingRowColors(True)
        self.sets_table.verticalHeader().setVisible(False)
        self.sets_table.setShowGrid(False)
        self.sets_table.itemSelectionChanged.connect(self.on_table_selection_changed)
        
        # テーブルの行の高さを固定
        self.sets_table.verticalHeader().setDefaultSectionSize(self.TABLE_ROW_HEIGHT)
        
        top_layout.addWidget(self.sets_table)
        frame_layout.addWidget(top_section)
        
        # 下部: 語彙とシステム指示の編集エリア
        editor_section = QWidget()
        editor_layout = QVBoxLayout(editor_section)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(int(AppTheme.SPACING_MD.replace("px", "")))
        
        # 編集エリアのセクションタイトル
        edit_title = QLabel(AppLabels.INSTRUCTION_SETS_EDIT_SECTION_TITLE)
        edit_title.setObjectName("sectionTitle")
        editor_layout.addWidget(edit_title)
        
        # タブウィジェットで語彙と指示を切り替え
        self.tab_widget = QTabWidget()
        
        # 語彙編集タブ
        vocab_widget = QWidget()
        vocab_layout = QVBoxLayout(vocab_widget)
        vocab_layout.setContentsMargins(
            int(AppTheme.SPACING_SM.replace("px", "")), 
            int(AppTheme.SPACING_MD.replace("px", "")), 
            int(AppTheme.SPACING_SM.replace("px", "")), 
            int(AppTheme.SPACING_SM.replace("px", ""))
        )
        
        self.vocabulary_edit = QTextEdit()
        self.vocabulary_edit.setPlaceholderText(AppLabels.VOCABULARY_PLACEHOLDER)
        self.vocabulary_edit.setMinimumHeight(200)
        vocab_layout.addWidget(self.vocabulary_edit)
        
        self.tab_widget.addTab(vocab_widget, AppLabels.VOCABULARY_DIALOG_TITLE)
        
        # システム指示編集タブ
        instr_widget = QWidget()
        instr_layout = QVBoxLayout(instr_widget)
        instr_layout.setContentsMargins(
            int(AppTheme.SPACING_SM.replace("px", "")), 
            int(AppTheme.SPACING_MD.replace("px", "")), 
            int(AppTheme.SPACING_SM.replace("px", "")), 
            int(AppTheme.SPACING_SM.replace("px", ""))
        )
        
        self.instructions_edit = QTextEdit()
        self.instructions_edit.setPlaceholderText(AppLabels.SYSTEM_INSTRUCTIONS_DIALOG_PLACEHOLDER)
        instr_layout.addWidget(self.instructions_edit)
        
        self.tab_widget.addTab(instr_widget, AppLabels.SYSTEM_INSTRUCTIONS_DIALOG_TITLE)
        
        editor_layout.addWidget(self.tab_widget)
        frame_layout.addWidget(editor_section)
        
        # ボタンボックス
        button_box = QDialogButtonBox()
        
        self.apply_button = QPushButton(AppLabels.APPLY_BUTTON)
        self.apply_button.setProperty("class", "primary")
        self.apply_button.clicked.connect(self.apply_changes)
        self.apply_button.setFixedWidth(self.BUTTON_WIDTH)
        button_box.addButton(self.apply_button, QDialogButtonBox.ButtonRole.ActionRole)
        
        self.ok_button = QPushButton(AppLabels.OK_BUTTON)
        self.ok_button.setProperty("class", "primary")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setFixedWidth(self.BUTTON_WIDTH)
        button_box.addButton(self.ok_button, QDialogButtonBox.ButtonRole.AcceptRole)
        
        self.cancel_button = QPushButton(AppLabels.CANCEL_BUTTON)
        self.cancel_button.setProperty("class", "secondary")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setFixedWidth(self.BUTTON_WIDTH)
        button_box.addButton(self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole)
        
        frame_layout.addWidget(button_box)
        
        # メインレイアウトにダイアログフレームを追加
        main_layout.addWidget(dialog_frame)
        
        # 各セクションの高さ比率を設定
        frame_layout.setStretch(2, 5)  # テーブル部分
        frame_layout.setStretch(3, 4)  # 編集部分
    
    def update_table_view(self):
        """テーブルビューを最新の状態に更新"""
        # テーブルをクリア
        self.sets_table.setRowCount(0)
        
        # セットがない場合は早期リターン
        if not self.manager.sets:
            return
        
        # 各セットの情報をテーブルに追加
        for i, instruction_set in enumerate(self.manager.sets):
            # 新しい行を追加
            row_position = self.sets_table.rowCount()
            self.sets_table.insertRow(row_position)
            
            # 名前列
            name_item = QTableWidgetItem(instruction_set.name)
            
            # 現在アクティブなセットであればボールド体にして色を変更
            if instruction_set == self.manager.active_set:
                font = QFont()
                font.setBold(True)
                name_item.setFont(font)
                name_item.setForeground(QColor(AppTheme.PRIMARY))
                
                # アクティブセットの表示を変更
                name_item = QTableWidgetItem(f"✓ {instruction_set.name} ({AppLabels.INSTRUCTION_SETS_ACTIVE_MARK})")
                name_item.setFont(font)
                name_item.setForeground(QColor(AppTheme.PRIMARY))
            
            self.sets_table.setItem(row_position, 0, name_item)
            
            # 語彙列のテキスト作成
            vocab_text = self._format_vocabulary_preview(instruction_set.vocabulary)
            vocab_item = QTableWidgetItem(vocab_text)
            self.sets_table.setItem(row_position, 1, vocab_item)
            
            # 指示列のテキスト作成
            instr_text = self._format_instructions_preview(instruction_set.instructions)
            instr_item = QTableWidgetItem(instr_text)
            self.sets_table.setItem(row_position, 2, instr_item)
            
            # アクティブセットの行に背景色を設定
            if instruction_set == self.manager.active_set:
                for col in range(3):
                    self.sets_table.item(row_position, col).setBackground(QColor(AppTheme.SELECTION))
                    
    def _format_vocabulary_preview(self, vocabulary_list):
        """語彙リストのプレビュー用フォーマット"""
        if not vocabulary_list:
            return ""
            
        # 長すぎる場合は省略
        MAX_PREVIEW_ITEMS = 3
        
        vocab_preview = ", ".join(vocabulary_list[:MAX_PREVIEW_ITEMS])
        if len(vocabulary_list) > MAX_PREVIEW_ITEMS:
            vocab_preview += f" ... ({len(vocabulary_list)}項目)"
        return vocab_preview
        
    def _format_instructions_preview(self, instructions_list):
        """指示リストのプレビュー用フォーマット"""
        if not instructions_list:
            return ""
            
        # 長すぎる場合は省略
        MAX_PREVIEW_ITEMS = 2
        MAX_CHARS_PER_ITEM = 30
        
        # 各項目を適切な長さに切り詰める
        instr_preview = " / ".join([
            instr[:MAX_CHARS_PER_ITEM] + "..." if len(instr) > MAX_CHARS_PER_ITEM else instr 
            for instr in instructions_list[:MAX_PREVIEW_ITEMS]
        ])
        
        # 表示しきれない項目がある場合は省略表記を追加
        if len(instructions_list) > MAX_PREVIEW_ITEMS:
            instr_preview += f" ... ({len(instructions_list)}項目)"
            
        return instr_preview
    
    def get_selected_index(self):
        """現在選択されているセットのインデックスを取得"""
        selected_rows = self.sets_table.selectionModel().selectedRows()
        if not selected_rows:
            return -1
        return selected_rows[0].row()
    
    def on_table_selection_changed(self):
        """テーブルの選択変更時のハンドラ"""
        selected_index = self.get_selected_index()
        
        # スタイル設定 - 新しいスタイル適用方法
        primary_button_style = AppStyles.get_button_style("primary")
        
        # 選択されていない場合はコントロールを無効化
        if selected_index < 0:
            self.vocabulary_edit.setEnabled(False)
            self.instructions_edit.setEnabled(False)
            self.activate_button.setEnabled(False)
            self.rename_set_button.setEnabled(False)
            self.remove_set_button.setEnabled(False)
            self.apply_button.setEnabled(False)
            return
        
        # テキスト編集ウィジェットを有効化
        self.vocabulary_edit.setEnabled(True)
        self.instructions_edit.setEnabled(True)
        
        # 選択されたセットの情報を編集欄に表示
        selected_set = self.manager.sets[selected_index]
        self.vocabulary_edit.setText("\n".join(selected_set.vocabulary))
        self.instructions_edit.setText("\n".join(selected_set.instructions))
        
        # ボタンの有効化
        self.rename_set_button.setEnabled(True)
        self.apply_button.setEnabled(True)
        
        # セットが1つしかない場合は削除を無効化
        self.remove_set_button.setEnabled(len(self.manager.sets) > 1)
        
        # 選択されたセットがアクティブかどうかで状態を変更
        is_active = selected_set == self.manager.active_set
        if is_active:
            self.activate_button.setEnabled(False)
            self.activate_button.setText(AppLabels.INSTRUCTION_SETS_CURRENTLY_ACTIVE)
            # アクティブセットボタンのスタイル
            inactive_style = f"""
                QPushButton {{
                    background-color: {AppTheme.SUCCESS};
                    color: white;
                    border: none;
                    border-radius: {AppTheme.RADIUS_SM};
                    padding: {AppTheme.PADDING_MD};
                    min-width: 110px;
                    font-weight: bold;
                }}
                
                QPushButton:hover {{
                    background-color: {AppTheme.SUCCESS_HOVER};
                }}
            """
            self.activate_button.setStyleSheet(inactive_style)
        else:
            self.activate_button.setEnabled(True)
            self.activate_button.setText(AppLabels.INSTRUCTION_SETS_ACTIVATE_BUTTON)
            self.activate_button.setStyleSheet(primary_button_style)
    
    def activate_current_set(self):
        """現在選択されているセットをアクティブに設定"""
        index = self.get_selected_index()
        if index < 0:
            return
        
        # アクティブセットを設定
        self.manager.set_active(index)
        
        # テーブルを更新
        self.update_table_view()
    
    def add_new_set(self):
        """新しいセットを追加"""
        dialog = SimpleInputDialog(
            parent=self,
            title=AppLabels.INSTRUCTION_SETS_NEW_TITLE,
            prompt=AppLabels.INSTRUCTION_SETS_NEW_PROMPT
        )
        
        ok = dialog.exec()
        name = dialog.textValue()
        
        if ok and name:
            # 新しいセットを作成
            new_set = InstructionSet(name)
            index = self.manager.add_set(new_set)
            
            # テーブルを更新して新しいセットを選択
            self.update_table_view()
            self.sets_table.selectRow(index)
    
    def rename_selected_set(self):
        """選択されたセットの名前を変更"""
        index = self.get_selected_index()
        if index < 0:
            return
        
        current_name = self.manager.sets[index].name
        
        dialog = SimpleInputDialog(
            parent=self,
            title=AppLabels.INSTRUCTION_SETS_RENAME_TITLE,
            prompt=AppLabels.INSTRUCTION_SETS_RENAME_PROMPT,
            initial_text=current_name
        )
        
        ok = dialog.exec()
        name = dialog.textValue()
        
        if ok and name:
            # 名前を更新
            self.manager.sets[index].name = name
            
            # テーブルを更新
            self.update_table_view()
            self.sets_table.selectRow(index)
    
    def remove_selected_set(self):
        """選択されたセットを削除"""
        index = self.get_selected_index()
        if index < 0:
            return
        
        selected_set = self.manager.sets[index]
        
        # 確認ダイアログ
        confirmed = SimpleMessageDialog.show_confirmation(
            self,
            AppLabels.INSTRUCTION_SETS_REMOVE_TITLE,
            AppLabels.INSTRUCTION_SETS_REMOVE_CONFIRM.format(selected_set.name)
        )
        
        if confirmed:
            # アクティブセットが削除される場合の処理
            was_active = self.manager.active_set == selected_set
            
            # セットを削除
            self.manager.remove_set(index)
            
            # テーブルを更新
            self.update_table_view()
            
            # 削除後にテーブルに行が残っていれば、最初の行を選択
            if self.sets_table.rowCount() > 0:
                self.sets_table.selectRow(0)
    
    def apply_changes(self):
        """現在の変更を適用（アクティブセットを変更して保存）"""
        index = self.get_selected_index()
        if index < 0:
            return
        
        # 現在のセットを更新
        selected_set = self.manager.sets[index]
        
        # テキストエディタから値を取得
        vocab_text = self.vocabulary_edit.toPlainText().strip()
        vocab_list = [line.strip() for line in vocab_text.split('\n') if line.strip()]
        
        instr_text = self.instructions_edit.toPlainText().strip()
        instr_list = [line.strip() for line in instr_text.split('\n') if line.strip()]
        
        # セットを更新
        selected_set.vocabulary = vocab_list
        selected_set.instructions = instr_list
        
        # 保存
        self.manager.save_to_settings()
        
        # テーブルを更新
        self.update_table_view()
        
        # 更新を通知
        SimpleMessageDialog.show_message(
            self,
            AppLabels.INSTRUCTION_SETS_UPDATED_TITLE,
            AppLabels.INSTRUCTION_SETS_UPDATED_SUCCESS,
            SimpleMessageDialog.INFO
        )
    
    def accept(self):
        """OKボタンが押されたときの処理"""
        # 現在の変更を適用
        self.apply_changes()
        
        # ダイアログを閉じる
        super().accept()
    
    def get_manager(self) -> InstructionSetManager:
        """現在のInstructionSetManagerを返す"""
        return self.manager 