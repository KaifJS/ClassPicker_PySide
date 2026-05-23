# ui_main_window.py
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt
from ui_draw_page import DrawPage
from ui_settings_page import SettingsPage
from core import DrawCore
from music import MusicPlayer
import json
import os

class MainWindow(QMainWindow):
    def __init__(self, default_students=None):
        super().__init__()
        self.core = DrawCore()
        if default_students:
            self.core.load_students(default_students)
        self.music = MusicPlayer()
        self.settings = self.load_settings()
        self.music.enabled = self.settings.get('music_enabled', False)
        self.music.file = self.settings.get('music_file', '')
        self.music.volume = self.settings.get('music_volume', 0.5)
        self.setup_ui()
        self.setup_connections()

    def load_settings(self):
        default = {
            'result_font_size': 36,
            'result_font_family': 'Microsoft YaHei',
            'result_font_color': '#ffffff',
            'auto_save': True,
            'music_enabled': False,
            'music_volume': 0.5,
            'music_file': '',
            'theme': 'dark'
        }
        if os.path.exists('app_settings.json'):
            try:
                with open('app_settings.json', 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    default.update(saved)
            except:
                pass
        return default

    def save_settings(self):
        try:
            with open('app_settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except:
            pass

    def setup_ui(self):
        self.setWindowTitle("智能抽号系统 v3.0 - PySide6 完全版")
        self.resize(1300, 850)
        self.setMinimumSize(1100, 700)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 左侧导航栏
        nav_bar = QFrame()
        nav_bar.setFixedWidth(200)
        nav_bar.setObjectName("navBar")
        nav_bar.setStyleSheet("background-color: #2a2b3c; border-right: 1px solid #3a3b4c;")
        nav_layout = QVBoxLayout(nav_bar)
        nav_layout.setAlignment(Qt.AlignTop)
        nav_layout.setSpacing(20)
        nav_layout.setContentsMargins(20, 40, 20, 40)

        logo = QLabel("✨ 随机抽号")
        logo.setStyleSheet("font-size: 20px; font-weight: bold; color: #60a5fa;")
        logo.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(logo)

        self.nav_btns = []
        nav_items = [("🎲 抽号", 0), ("⚙️ 设置", 1)]
        for text, idx in nav_items:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #cbd5e1;
                    font-size: 16px;
                    text-align: left;
                    padding: 12px 16px;
                    border-radius: 12px;
                }
                QPushButton:hover { background-color: #3b3c4e; color: white; }
            """)
            btn.clicked.connect(lambda checked, i=idx: self.stacked.setCurrentIndex(i))
            nav_layout.addWidget(btn)
            self.nav_btns.append(btn)
        nav_layout.addStretch()

        # 右侧堆叠区
        self.stacked = QStackedWidget()
        self.draw_page = DrawPage(self.core, self.music, self.settings, self.save_settings)
        # 修改：增加最后一个参数 self.draw_page，以便设置页面可以访问抽号页面
        self.settings_page = SettingsPage(self.core, self.settings, self.save_settings, self.draw_page.update_status, self.draw_page)
        self.stacked.addWidget(self.draw_page)
        self.stacked.addWidget(self.settings_page)

        main_layout.addWidget(nav_bar)
        main_layout.addWidget(self.stacked, 1)

        # 初始选中抽号页
        self.stacked.setCurrentIndex(0)
        self.nav_btns[0].setStyleSheet("background-color: #3b3c4e; color: white; border-radius: 12px;")

    def setup_connections(self):
        self.stacked.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        for i, btn in enumerate(self.nav_btns):
            if i == index:
                btn.setStyleSheet("background-color: #3b3c4e; color: white; border-radius: 12px;")
            else:
                btn.setStyleSheet("background-color: transparent; color: #cbd5e1; font-size: 16px; text-align: left; padding: 12px 16px; border-radius: 12px;")