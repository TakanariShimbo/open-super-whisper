"""
アプリケーションのスタイル定義モジュール

このモジュールには、アプリケーションのUI全体で使用されるスタイルシートが含まれています。
スタイルの一元管理により、見た目の一貫性とメンテナンスが容易になります。
"""

class AppTheme:
    """
    アプリケーションのテーマ定義クラス
    
    このクラスはアプリケーション全体で使用されるテーマ要素（色、サイズ、間隔など）を定義します。
    テーマの一元管理により、全体的な外観の調整が容易になります。
    """
    
    # ==================== カラーテーマ ====================
    
    # 基本カラー
    PRIMARY = "#4A76E8"
    PRIMARY_HOVER = "#3A66D8"
    PRIMARY_PRESSED = "#2A56C8"
    
    DANGER = "#E74C3C"
    DANGER_HOVER = "#D73C2C"
    DANGER_PRESSED = "#C72C1C"
    
    SUCCESS = "#2ECC71"
    SUCCESS_HOVER = "#27AE60"
    
    WARNING = "#F39C12"
    WARNING_HOVER = "#E67E22"
    
    # 背景・表面・ボーダー
    BACKGROUND = "#F8F9FC"
    SURFACE = "#FFFFFF"
    BORDER = "#E2E6EC"
    BORDER_HOVER = "#C5CFDC"
    
    # テキスト
    TEXT_PRIMARY = "#333333"
    TEXT_SECONDARY = "#555555"
    TEXT_DISABLED = "#999999"
    TEXT_INVERSE = "#FFFFFF"
    
    # 状態
    SELECTION = "#EBF0FF"
    TITLE = "#324275"
    
    # ==================== サイズテーマ ====================
    
    # ウィンドウサイズ
    MAIN_WINDOW_WIDTH = 1200
    MAIN_WINDOW_HEIGHT = 600
    
    # レイアウトの余白と間隔
    MAIN_MARGIN = 15
    MAIN_SPACING = 15
    PANEL_MARGIN = 15
    PANEL_SPACING = 15
    FORM_HORIZONTAL_SPACING = 12
    FORM_VERTICAL_SPACING = 12
    
    # パディング（内部余白）
    PADDING_XS = "2px 4px"
    PADDING_SM = "5px 10px"
    PADDING_MD = "8px 16px"
    PADDING_LG = "12px 24px"
    
    # ボーダー半径
    RADIUS_XS = "3px"
    RADIUS_SM = "5px"
    RADIUS_MD = "7px"
    RADIUS_LG = "10px"
    RADIUS_ROUND = "20px"
    
    # フォントサイズ
    FONT_XS = "11px"
    FONT_SM = "12px"
    FONT_MD = "13px"
    FONT_LG = "15px"
    FONT_XL = "16px"
    
    # コンポーネントサイズ
    BUTTON_HEIGHT_SM = "30px"
    BUTTON_HEIGHT_MD = "36px"
    BUTTON_HEIGHT_LG = "44px"
    
    BUTTON_WIDTH_SM = "80px"
    BUTTON_WIDTH_MD = "110px"
    BUTTON_WIDTH_LG = "150px"
    
    ICON_SIZE_SM = "16px"
    ICON_SIZE_MD = "18px"
    ICON_SIZE_LG = "24px"
    
    # 間隔
    SPACING_XS = "4px"
    SPACING_SM = "8px"
    SPACING_MD = "16px"
    SPACING_LG = "24px"
    
    # ==================== フォント ====================
    FONT_FAMILY = "\"Yu Gothic UI\", \"Segoe UI\", Arial, sans-serif"
    FONT_FAMILY_MONO = "\"Roboto Mono\", Consolas, monospace"
    
    @classmethod
    def lighten(cls, color, percent=10):
        """色を明るくする"""
        import colorsys
        # 16進数からRGB変換
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16) / 255.0, int(color[2:4], 16) / 255.0, int(color[4:6], 16) / 255.0
        # HSL変換して明度を調整
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        l = min(1.0, l + (percent / 100.0))
        # RGBに戻して16進数に変換
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    
    @classmethod
    def darken(cls, color, percent=10):
        """色を暗くする"""
        return cls.lighten(color, -percent)
    
    @classmethod
    def get_dark_theme(cls):
        """ダークテーマのカラー取得"""
        dark = cls()
        # 基本色の反転
        dark.BACKGROUND = "#1E1E1E"
        dark.SURFACE = "#2D2D2D"
        dark.BORDER = "#444444"
        dark.BORDER_HOVER = "#555555"
        dark.TEXT_PRIMARY = "#EEEEEE"
        dark.TEXT_SECONDARY = "#AAAAAA"
        dark.SELECTION = "#3A3D41"
        # 他の色は調整が必要
        return dark

class StyleSheet:
    """
    スタイルシート生成クラス
    
    このクラスはテーマに基づいたスタイルシートを生成します。
    各UIコンポーネントの基本スタイルを定義し、組み合わせて完全なスタイルシートを作成します。
    """
    
    def __init__(self, theme=None):
        """テーマを指定してスタイルシートを初期化"""
        self.theme = theme or AppTheme
    
    def _replace_vars(self, style_str):
        """スタイル文字列内のテーマ変数を置換"""
        # すべてのテーマ変数を取得
        for attr in dir(self.theme):
            if attr.isupper() and not attr.startswith('_'):
                value = getattr(self.theme, attr)
                if isinstance(value, str):
                    # スタイル文字列内のすべての %VARIABLE% を実際の値に置換
                    style_str = style_str.replace(f"%{attr}%", value)
        return style_str
    
    # ベーススタイル - すべてのスタイルの基盤
    def base(self):
        """基本スタイル - フォントとカラー設定"""
        return self._replace_vars(f"""
            * {{
                font-family: %FONT_FAMILY%;
                font-size: %FONT_MD%;
                color: %TEXT_PRIMARY%;
            }}
            
            QMainWindow, QDialog {{
                background-color: %BACKGROUND%;
            }}
        """)
    
    # ボタンスタイル
    def button(self, variant="primary", size="md"):
        """ボタンの基本スタイル"""
        # サイズに応じた設定を選択
        if size == "sm":
            padding = self.theme.PADDING_SM
            font_size = self.theme.FONT_SM
            height = self.theme.BUTTON_HEIGHT_SM
            min_width = self.theme.BUTTON_WIDTH_SM
        elif size == "lg":
            padding = self.theme.PADDING_LG
            font_size = self.theme.FONT_LG
            height = self.theme.BUTTON_HEIGHT_LG
            min_width = self.theme.BUTTON_WIDTH_LG
        else:  # md（デフォルト）
            padding = self.theme.PADDING_MD
            font_size = self.theme.FONT_MD
            height = self.theme.BUTTON_HEIGHT_MD
            min_width = self.theme.BUTTON_WIDTH_MD
        
        # 基本ボタンスタイル
        base_style = f"""
            QPushButton {{
                padding: {padding};
                border-radius: %RADIUS_SM%;
                font-weight: bold;
                font-size: {font_size};
                min-width: {min_width};
                height: {height};
            }}
            
            QPushButton:disabled {{
                opacity: 0.6;
            }}
        """
        
        # バリアントに応じたスタイル
        if variant == "primary":
            style = base_style + """
                QPushButton {
                    background-color: %PRIMARY%;
                    color: white;
                    border: none;
                }
                
                QPushButton:hover {
                    background-color: %PRIMARY_HOVER%;
                }
                
                QPushButton:pressed {
                    background-color: %PRIMARY_PRESSED%;
                }
            """
        elif variant == "danger":
            style = base_style + """
        QPushButton {
                    background-color: %DANGER%;
            color: white;
            border: none;
        }
        
        QPushButton:hover {
                    background-color: %DANGER_HOVER%;
        }
        
        QPushButton:pressed {
                    background-color: %DANGER_PRESSED%;
                }
            """
        elif variant == "secondary":
            style = base_style + """
                QPushButton {
                    background-color: %BACKGROUND%;
                    color: %TEXT_PRIMARY%;
                    border: 1px solid %BORDER%;
                }
                
                QPushButton:hover {
            background-color: #E8ECF2;
                    border-color: %BORDER_HOVER%;
        }
        
                QPushButton:pressed {
            background-color: #D8DDE8;
        }
            """
        else:  # テキストボタン
            style = base_style + """
                QPushButton {
                    background-color: transparent;
                    color: %PRIMARY%;
                    border: none;
                }
                
                QPushButton:hover {
                    color: %PRIMARY_HOVER%;
                    text-decoration: underline;
                }
                
                QPushButton:pressed {
                    color: %PRIMARY_PRESSED%;
                }
            """
            
        return self._replace_vars(style)
    
    # 入力フィールドスタイル
    def input(self, multiline=False):
        """入力フィールドのスタイル"""
        base_style = """
            QLineEdit, QTextEdit, QPlainTextEdit {
                border: 1px solid %BORDER%;
                border-radius: %RADIUS_SM%;
                padding: 8px;
                background-color: %SURFACE%;
                color: %TEXT_PRIMARY%;
            }
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
                border-color: %PRIMARY%;
            }
            
            QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
                background-color: #F5F5F5;
                color: %TEXT_DISABLED%;
                border-color: #D0D0D0;
            }
        """
        
        if multiline:
            style = base_style + """
                QTextEdit, QPlainTextEdit {
                    font-size: %FONT_MD%;
                    line-height: 1.4;
                }
            """
        else:
            style = base_style + """
                QLineEdit {
                    font-size: %FONT_MD%;
                    height: 20px;
                }
            """
            
        return self._replace_vars(style)
    
    # リストとテーブルスタイル
    def list_view(self):
        """リストウィジェットのスタイル"""
        return self._replace_vars("""
            QListWidget, QListView {
                border: 1px solid %BORDER%;
                border-radius: %RADIUS_SM%;
                background-color: %SURFACE%;
            padding: 4px;
        }
        
            QListWidget::item, QListView::item {
            padding: 6px;
            border-bottom: 1px solid #F2F4F8;
        }
        
            QListWidget::item:selected, QListView::item:selected {
                background-color: %SELECTION%;
                color: %PRIMARY%;
            border-radius: 2px;
        }
        """)
    
    def table_view(self):
        """テーブルウィジェットのスタイル"""
        return self._replace_vars("""
            QTableWidget, QTableView {
                border: 1px solid %BORDER%;
                border-radius: %RADIUS_SM%;
                background-color: %SURFACE%;
                alternate-background-color: #F5F8FF;
                gridline-color: #F0F3F9;
                selection-background-color: %SELECTION%;
                selection-color: %TEXT_PRIMARY%;
            }
            
            QTableWidget::item, QTableView::item {
                padding: 7px;
                border-bottom: 1px solid #F0F3F9;
            }
            
            QTableWidget::item:selected, QTableView::item:selected {
                background-color: %SELECTION%;
                color: %PRIMARY%;
            }
            
            QHeaderView::section {
                background-color: #E8ECF2;
                padding: 8px;
            border: none;
                border-right: 1px solid #D8DDE8;
                border-bottom: 1px solid #D8DDE8;
                font-weight: bold;
                color: %TEXT_PRIMARY%;
            }
        """)
    
    # タブスタイル
    def tab_widget(self):
        """タブウィジェットのスタイル"""
        return self._replace_vars("""
            QTabWidget::pane {
                border: 1px solid %BORDER%;
                border-radius: %RADIUS_SM%;
                background-color: %SURFACE%;
                top: -1px;
            }
            
            QTabBar::tab {
                background-color: #E8ECF2;
                border: 1px solid %BORDER%;
                border-bottom: none;
                border-top-left-radius: %RADIUS_SM%;
                border-top-right-radius: %RADIUS_SM%;
                padding: 8px 14px;
                margin-right: 2px;
                min-width: 80px;
                font-weight: normal;
            }
            
            QTabBar::tab:selected {
                background-color: %SURFACE%;
                border-bottom: 2px solid %PRIMARY%;
                color: %PRIMARY%;
            font-weight: bold;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #EFF2F7;
            }
        """)
    
    # その他のスタイル
    def toolbar(self):
        """ツールバーのスタイル"""
        return self._replace_vars("""
            QToolBar {
                background-color: %SURFACE%;
                border-bottom: 1px solid #E8ECF2;
                spacing: 5px;
                padding: 5px;
            }
            
            QToolBar QToolButton {
                padding: 5px 8px;
                border-radius: 3px;
                margin: 1px;
            }
            
            QToolBar QToolButton:checked {
                background-color: %PRIMARY%;
                color: white;
                font-weight: bold;
            }
            
            QToolBar QToolButton:hover {
                background-color: %SELECTION%;
            }
            
            QToolBar QToolButton:checked:hover {
                background-color: %PRIMARY_HOVER%;
            }
            
            QToolBar QToolButton:pressed {
                background-color: %PRIMARY_HOVER%;
                color: white;
            }
        """)
    
    def menu(self):
        """メニューのスタイル"""
        return self._replace_vars("""
            QMenu {
                background-color: %SURFACE%;
                border: 1px solid %BORDER%;
                padding: 2px;
            }
            
            QMenu::item {
                padding: 6px 24px;
                margin: 2px 4px;
            }
            
            QMenu::item:selected {
                background-color: %PRIMARY%;
                color: white;
                border-radius: 3px;
            }
            
            QMenu::separator {
                height: 1px;
                background-color: %BORDER%;
                margin: 3px 8px;
            }
        """)
    
    def status_bar(self):
        """ステータスバーのスタイル"""
        return self._replace_vars("""
            QStatusBar {
                background-color: %SURFACE%;
                color: %TEXT_SECONDARY%;
                border-top: 1px solid #E8ECF2;
            }
        """)
    
    def combo_box(self):
        """コンボボックスのスタイル"""
        return self._replace_vars("""
            QComboBox {
                border: 1px solid %BORDER%;
                border-radius: %RADIUS_SM%;
                padding: 6px 12px;
                background-color: %SURFACE%;
                min-width: 150px;
            }
            
            QComboBox:hover {
                border-color: %BORDER_HOVER%;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 20px;
                border-left: none;
            }
            
            QComboBox QAbstractItemView {
                background-color: %SURFACE%;
                border: 1px solid %BORDER%;
                selection-background-color: %PRIMARY%;
                selection-color: white;
            }
        """)
    
    def panel(self):
        """パネルウィジェットのスタイル"""
        return self._replace_vars("""
            QWidget#panel {
                background-color: %SURFACE%;
                border-radius: %RADIUS_LG%;
                border: 1px solid %BORDER%;
            }
        """)
    
    # レコーディングインジケーター特殊スタイル
    def recording_indicator(self, state="normal"):
        """録音インジケーターのスタイル"""
        if state == "active":
            return self._replace_vars("""
        #statusFrame {
            border-radius: 12px;
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 rgba(224, 82, 82, 220), 
                                        stop:1 rgba(200, 60, 60, 220));
            border: 1px solid rgba(255, 255, 255, 60);
        }
        
        #statusLabel {
            color: white;
            font-weight: bold;
            font-size: 15px;
            margin-top: 2px;
            padding: 2px;
        }
        
        #infoLabel {
            color: white;
            font-weight: bold;
            font-size: 12px;
            margin-top: 2px;
            padding: 2px;
        }
        
        #timerLabel {
            color: white;
            font-size: 20px;
            font-weight: 500;
            padding: 2px;
        }
            """)
        elif state == "transcribing":
            return self._replace_vars("""
        #statusFrame {
            border-radius: 12px;
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 rgba(120, 120, 120, 220), 
                                    stop:1 rgba(90, 90, 90, 220));
            border: 1px solid rgba(255, 255, 255, 60);
        }
        
        #statusLabel {
            color: white;
            font-weight: bold;
            font-size: 15px;
            margin-top: 2px;
            padding: 2px;
        }
        
        #infoLabel {
            color: white;
            font-weight: bold;
            font-size: 12px;
            margin-top: 2px;
            padding: 2px;
        }
        
        #timerLabel {
            color: white;
            font-size: 20px;
            font-weight: 500;
            padding: 2px;
        }
            """)
        elif state == "transcribed":
            return self._replace_vars("""
        #statusFrame {
            border-radius: 12px;
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 rgba(65, 105, 225, 220), 
                                    stop:1 rgba(45, 85, 205, 220));
            border: 1px solid rgba(255, 255, 255, 60);
        }
        
        #statusLabel {
            color: white;
            font-weight: bold;
            font-size: 15px;
            margin-top: 2px;
            padding: 2px;
        }
        
        #infoLabel {
            color: white;
            font-weight: bold;
            font-size: 12px;
            margin-top: 2px;
            padding: 2px;
        }
        
        #timerLabel {
            color: white;
            font-size: 20px;
            font-weight: 500;
            padding: 2px;
        }
            """)
        else:  # normal
            return self._replace_vars("""
        #statusFrame {
            border-radius: 12px;
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(90, 100, 120, 220), 
                                stop:1 rgba(70, 78, 94, 220));
            border: 1px solid rgba(255, 255, 255, 60);
        }
        
        #statusLabel {
            color: white;
            font-weight: bold;
            font-size: 15px;
            margin-top: 2px;
            padding: 2px;
        }
        
        #infoLabel {
            color: white;
            font-weight: bold;
            font-size: 12px;
            margin-top: 2px;
            padding: 2px;
        }
        
        #timerLabel {
            color: white;
            font-size: 20px;
            font-weight: 500;
            padding: 2px;
        }
            """)
    
    # レコーディングボタン特殊スタイル
    def record_button(self, is_recording=False):
        """録音ボタンのスタイル"""
        if is_recording:
            return self._replace_vars("""
                #recordButton {
                    background-color: %DANGER%;
                    color: white;
                    border: none;
                    border-radius: %RADIUS_MD%;
                    padding: 10px 24px;
                    font-weight: bold;
                    font-size: 15px;
                }
                
                #recordButton:hover {
                    background-color: %DANGER_HOVER%;
                }
                
                #recordButton:pressed {
                    background-color: %DANGER_PRESSED%;
                }
            """)
        else:
            return self._replace_vars("""
                #recordButton {
                    background-color: %PRIMARY%;
            color: white;
                    border: none;
                    border-radius: %RADIUS_MD%;
                    padding: 10px 24px;
                    font-weight: bold;
                    font-size: 15px;
                }
                
                #recordButton:hover {
                    background-color: %PRIMARY_HOVER%;
                }
                
                #recordButton:pressed {
                    background-color: %PRIMARY_PRESSED%;
                }
            """)
    
    # ダイアログ関連の共通スタイル定数
    DIALOG_BORDER_RADIUS = f"border-radius: {AppTheme.RADIUS_MD};"
    DIALOG_BACKGROUND = f"background-color: {AppTheme.SURFACE};"
    DIALOG_BORDER = f"border: 1px solid {AppTheme.BORDER};"
    DIALOG_PADDING = f"padding: {AppTheme.PADDING_MD};"
    DIALOG_MARGIN = f"margin: {AppTheme.SPACING_MD};"
    
    DIALOG_FRAME_STYLE = f"{DIALOG_BACKGROUND} {DIALOG_BORDER} {DIALOG_BORDER_RADIUS} {DIALOG_PADDING}"
    DIALOG_BUTTON_BOX_STYLE = f"margin-top: {AppTheme.SPACING_MD};"
    
    def dialog_style(self, dialog_type="default"):
        """ダイアログのスタイル"""
        base_style = self._replace_vars("""
            QDialog {
                background-color: %BACKGROUND%;
            }
            
            QDialogButtonBox {
                margin-top: %SPACING_MD%;
            }
            
            #dialogFrame {
                background-color: %SURFACE%;
                border: 1px solid %BORDER%;
                border-radius: %RADIUS_MD%;
                padding: %PADDING_MD%;
            }
            
            QLabel#dialogTitle {
                font-weight: bold;
                font-size: %FONT_LG%;
                color: %TITLE%;
                margin-bottom: 10px;
            }
            
            QLabel#sectionTitle {
                font-weight: bold;
                font-size: %FONT_MD%;
                color: %PRIMARY%;
                margin-top: 10px;
            }
            
            #separatorLine {
                background-color: %BORDER%;
                border: none;
        }
        
        QPushButton {
                min-width: %BUTTON_WIDTH_MD%;
                font-weight: bold;
                padding: %PADDING_SM%;
                border-radius: %RADIUS_SM%;
            }
            
            QPushButton[class="primary"] {
                background-color: %PRIMARY%;
            color: white;
            border: none;
            }
            
            QPushButton[class="primary"]:hover {
                background-color: %PRIMARY_HOVER%;
            }
            
            QPushButton[class="primary"]:pressed {
                background-color: %PRIMARY_PRESSED%;
            }
            
            QPushButton[class="danger"] {
                background-color: %DANGER%;
                color: white;
                border: none;
            }
            
            QPushButton[class="danger"]:hover {
                background-color: %DANGER_HOVER%;
            }
            
            QPushButton[class="danger"]:pressed {
                background-color: %DANGER_PRESSED%;
            }
            
            QPushButton[class="secondary"] {
                background-color: %BACKGROUND%;
                color: %TEXT_PRIMARY%;
                border: 1px solid %BORDER%;
            }
            
            QPushButton[class="secondary"]:hover {
                background-color: #E8ECF2;
                border-color: %BORDER_HOVER%;
            }
            
            QPushButton[class="secondary"]:pressed {
                background-color: #D8DDE8;
            }
            
            QTableWidget {
                border: 1px solid %BORDER%;
                border-radius: %RADIUS_SM%;
                background-color: %SURFACE%;
                alternate-background-color: #F5F8FF;
                gridline-color: #F0F3F9;
                selection-background-color: %SELECTION%;
                selection-color: %TEXT_PRIMARY%;
            }
            
            QTableWidget::item {
                padding: 7px;
                border-bottom: 1px solid #F0F3F9;
            }
            
            QTableWidget::item:selected {
                background-color: %SELECTION%;
                color: %PRIMARY%;
            }
            
            QHeaderView::section {
                background-color: #E8ECF2;
                padding: 8px;
            border: none;
                border-right: 1px solid #D8DDE8;
                border-bottom: 1px solid #D8DDE8;
            font-weight: bold;
                color: %TEXT_PRIMARY%;
            }
            
            QTabWidget::pane {
                border: 1px solid %BORDER%;
                border-radius: %RADIUS_SM%;
                background-color: %SURFACE%;
                top: -1px;
            }
            
            QTabBar::tab {
                background-color: #E8ECF2;
                border: 1px solid %BORDER%;
                border-bottom: none;
                border-top-left-radius: %RADIUS_SM%;
                border-top-right-radius: %RADIUS_SM%;
                padding: 8px 14px;
                margin-right: 2px;
                min-width: 80px;
                font-weight: normal;
            }
            
            QTabBar::tab:selected {
                background-color: %SURFACE%;
                border-bottom: 2px solid %PRIMARY%;
                color: %PRIMARY%;
            font-weight: bold;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #EFF2F7;
            }
            
            QLineEdit, QTextEdit, QPlainTextEdit {
                border: 1px solid %BORDER%;
                border-radius: %RADIUS_SM%;
                padding: 8px;
                background-color: %SURFACE%;
                color: %TEXT_PRIMARY%;
            }
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
                border-color: %PRIMARY%;
            }
        """)
        
        return base_style
    
    def main_window_style(self):
        """メインウィンドウのスタイルを取得"""
        style = self.base()
        style += self.toolbar()
        style += self.menu()
        style += self.status_bar()
        style += self.button("primary")
        style += self.input(multiline=True)
        style += self.combo_box()
        return style

class AppStyles:
    """
    アプリケーションスタイル管理クラス
    
    このクラスはアプリケーション全体のスタイルを管理します。
    テーマと連携して、すべてのUIコンポーネントに一貫したスタイルを提供します。
    """
    
    # スタイルシートジェネレーター
    _style_sheet = StyleSheet(AppTheme)
    
    # ================== インラインスタイル（直接使用可能） ==================
    SECTION_TITLE_STYLE = f"font-weight: bold; font-size: {AppTheme.FONT_LG}; color: {AppTheme.PRIMARY}; margin-bottom: 5px;"
    DIALOG_TITLE_STYLE = f"font-weight: bold; font-size: {AppTheme.FONT_LG}; color: {AppTheme.TITLE}; margin-bottom: 5px;"
    INFO_LABEL_STYLE = f"color: {AppTheme.TEXT_SECONDARY}; font-size: {AppTheme.FONT_MD};"
    
    @classmethod
    def set_theme(cls, theme):
        """テーマを変更する"""
        cls._style_sheet = StyleSheet(theme)
    
    @classmethod
    def get_button_style(cls, variant="primary", size="md"):
        """ボタンスタイルを取得"""
        return cls._style_sheet.button(variant, size)
    
    @classmethod
    def get_input_style(cls, multiline=False):
        """入力フィールドスタイルを取得"""
        return cls._style_sheet.input(multiline)
    
    @classmethod
    def get_dialog_style(cls, dialog_type="default"):
        """ダイアログスタイルを取得"""
        return cls._style_sheet.dialog_style(dialog_type)
    
    @classmethod
    def get_main_window_style(cls):
        """メインウィンドウスタイルを取得"""
        return cls._style_sheet.main_window_style()
    
    @classmethod
    def get_recording_indicator_style(cls, state="normal"):
        """録音インジケータースタイルを取得"""
        return cls._style_sheet.recording_indicator(state)
    
    @classmethod
    def get_record_button_style(cls, is_recording=False):
        """録音ボタンスタイルを取得"""
        return cls._style_sheet.record_button(is_recording)
    
    @classmethod
    def get_table_style(cls):
        """テーブルスタイルを取得"""
        return cls._style_sheet.table_view()
    
    @classmethod
    def get_list_style(cls):
        """リストスタイルを取得"""
        return cls._style_sheet.list_view()
    
    @classmethod
    def get_tab_style(cls):
        """タブスタイルを取得"""
        return cls._style_sheet.tab_widget()
    
    @classmethod
    def get_panel_style(cls, panel_type="default"):
        """パネルスタイルを取得"""
        return cls._style_sheet.panel()
    
    @classmethod
    def get_combobox_style(cls):
        """コンボボックススタイルを取得"""
        return cls._style_sheet.combo_box()
    
    @classmethod
    def get_label_style(cls, label_type="default"):
        """ラベルスタイルを取得"""
        if label_type == "section_title":
            return cls.SECTION_TITLE_STYLE
        elif label_type == "dialog_title":
            return cls.DIALOG_TITLE_STYLE
        elif label_type == "info":
            return cls.INFO_LABEL_STYLE
        elif label_type == "form":
            return f"color: {AppTheme.TEXT_PRIMARY}; font-size: {AppTheme.FONT_MD};"
        else:
            return f"color: {AppTheme.TEXT_PRIMARY};"
    
    @classmethod
    def get_text_edit_style(cls):
        """テキストエディットスタイルを取得"""
        return cls.get_input_style(multiline=True)
    
    @classmethod
    def get_timer_label_style(cls):
        """タイマーラベルスタイルを取得"""
        return f"color: {AppTheme.TEXT_PRIMARY}; font-size: {AppTheme.FONT_MD};"
    
    @classmethod
    def get_statusbar_style(cls):
        """ステータスバースタイルを取得"""
        return cls._style_sheet.status_bar()
    
    @classmethod
    def get_toolbar_style(cls):
        """ツールバースタイルを取得"""
        return cls._style_sheet.toolbar()
    
    @classmethod
    def get_system_tray_menu_style(cls):
        """システムトレイメニュースタイルを取得"""
        return cls._style_sheet.menu()
    
    @classmethod
    def get_color(cls, name):
        """テーマ色を取得"""
        return getattr(AppTheme, name.upper(), None)