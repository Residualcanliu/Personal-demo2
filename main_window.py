# 软件整体框架
import os
os.environ["AKSHARE_JS_ENGINE"] = "nodejs"
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QPushButton, QLabel, QStackedWidget, QSpacerItem,
                             QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont,QFontDatabase
from home_page import HomePage
from module1_chat import Module1Interface
from module2_compliance import Module2Interface
from module3_evaluation import Module3Interface
from module4_prediction import Module4Interface
from utils import get_resource_path
from PyQt6.QtGui import QPixmap

class SidebarButton(QPushButton):
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(parent)               # 关键：只传递 parent
        self.setText(f"  {icon_text}  {text}")
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 12px 16px;
                border: none;
                border-radius: 10px;
                background-color: transparent;
                color: #666666;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:checked {
                background-color: #D4AF37;
                color: #FFFFFF;
                font-weight: 600;
            }
            QPushButton:hover:!checked {
                background-color: #FCF3DC;
                color: #D4AF37;
            }
        """)
        self.setMinimumHeight(44)
    
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智能企业融资风险中控服务系统")
        self.setMinimumSize(1200, 800)
        self.resize(1280, 720)
        self._load_custom_fonts()
        self._init_ui()
        self._apply_global_style()

    def _load_custom_fonts(self):
        font_path = get_resource_path("fonts/SIMHEI.ttf")
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)
        sun_path = get_resource_path("fonts/SIMSUN.ttc")
        if os.path.exists(sun_path):
            QFontDatabase.addApplicationFont(sun_path)

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar, stretch=1)

        self.stacked_widget = QStackedWidget()
        self.home_page = HomePage()
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(Module1Interface())
        self.stacked_widget.addWidget(Module2Interface())
        self.stacked_widget.addWidget(Module3Interface())
        self.stacked_widget.addWidget(Module4Interface())
        main_layout.addWidget(self.stacked_widget, stretch=4)

        self.home_page.navigate_to_module.connect(self.on_navigate_request)

    def _create_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet("""
    background-color: #FFFDF5;
    border-right: 1px solid #E8D5A3;
""")
        sidebar.setMinimumWidth(260)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(10)

        logo_label = QLabel("🏦 融智风控")
        font = QFont("SimHei", 28, QFont.Weight.Bold)
        logo_label.setFont(font)
        logo_label.setStyleSheet("color: #0F3460; margin-bottom: 40px;")
        logo_label.setMinimumHeight(80)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        menu_items = [
            ("首页", "🏠"),
            ("智能对话", "💬"),
            ("合规分析", "📋"),
            ("融资评估", "📊"),
            ("涨跌预测", "📈"),
        ]
        self.buttons = []
        for idx, (text, icon) in enumerate(menu_items):
            btn = SidebarButton(text, icon)
            if idx == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, i=idx: self.on_sidebar_click(i))
            layout.addWidget(btn)
            self.buttons.append(btn)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        logout_btn = QPushButton("  🚪  退出")
        logout_btn.setStyleSheet("""
    QPushButton {
        text-align: left;
        padding: 12px 15px;
        border: none;
        border-radius: 8px;
        background-color: transparent;
        color: #64748B;
        font-size: 13px;
    }
    QPushButton:hover {
        background-color: #F5EEDC;
        color: #D4AF37;
    }
""")
        logout_btn.clicked.connect(self.close)
        logout_btn.setMinimumHeight(40)
        layout.addWidget(logout_btn)
        return sidebar

    def on_sidebar_click(self, index):
        self.stacked_widget.setCurrentIndex(index)
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)

    def on_navigate_request(self, index):
        self.stacked_widget.setCurrentIndex(index)
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)

    def _apply_global_style(self):
        self.setStyleSheet("""
    /* ===== 主窗口背景 ===== */
    QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #C9A96E, stop:0.5 #E0C87C, stop:1 #F2DEB0);
}

    /* ===== 通用按钮样式 ===== */
    QPushButton {
        background-color: #FFFDF5;
        border: 1px solid #E8D5A3;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 13px;
        color: #333333;
        font-weight: 500;
    }
    QPushButton:hover {
        background-color: #FFD700;
        border-color: #D4AF37;
        color: #FFFFFF;
    }
    QPushButton:pressed {
        background-color: #B8860B;
        border-color: #D4AF37;
        color: #FFFFFF;
    }
    QPushButton:checked {
        background-color: #D4AF37;
        color: #FFFFFF;
        font-weight: bold;
    }

    /* ===== 文字标签 ===== */
    QLabel {
        color: #333333;
        font-size: 13px;
        background-color: transparent;
    }
    QLabel#SecondaryText {
        color: #666666;
    }

    /* ===== 输入框/下拉框 ===== */
    QLineEdit, QTextEdit, QComboBox {
        border: 1px solid #D4AF37;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        color: #333333;
        background-color: #FFFFFF;
        selection-background-color: #D4AF37;
    }
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
        border-color: #FFD700;
    }

    /* ===== 表格表头 ===== */
    QHeaderView::section {
        background-color: #FDF8ED;
        color: #333333;
        font-weight: bold;
        border: none;
        border-bottom: 2px solid #D4AF37;
        padding: 10px 8px;
        font-size: 13px;
    }

    /* ===== 表格整体 ===== */
    QTableWidget {
        background-color: #FFFDF5;
        border: 1px solid #E8D5A3;
        gridline-color: #F5DEB3;
        alternate-background-color: #FFFFFF;
    }
    QTableWidget::item {
        padding: 8px;
        border-bottom: 1px solid #F5DEB3;
        color: #333333;
    }
    QTableWidget::item:hover {
        background-color: #FCF3DC;
    }
    QTableWidget::item:selected {
        background-color: #D4AF37;
        color: #FFFFFF;
    }

    /* ===== 列表控件 ===== */
    QListWidget {
        background-color: #FFFDF5;
        border: 1px solid #E8D5A3;
        border-radius: 8px;
    }
    QListWidget::item {
        padding: 8px;
        border-bottom: 1px solid #F5DEB3;
        color: #333333;
    }
    QListWidget::item:hover {
        background-color: #FCF3DC;
    }
    QListWidget::item:selected {
        background-color: #D4AF37;
        color: #FFFFFF;
    }

    /* ===== 选项卡 ===== */
    QTabBar::tab {
        background: #FFFDF5;
        padding: 10px 20px;
        margin-right: 6px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        color: #666666;
        border: 1px solid #E8D5A3;
        border-bottom: none;
    }
    QTabBar::tab:selected {
        color: #D4AF37;
        font-weight: bold;
        background: #FDF8ED;
    }
    QTabBar::tab:hover:!selected {
        background-color: #FFD700;
        color: #FFFFFF;
    }

    /* ===== 卡片样式 ===== */
    QFrame#DashboardCard {
        background-color: #FFFDF5;
        border-radius: 16px;
        border: 1px solid #E8D5A3;
    }
    QFrame#DashboardCard:hover {
        border-color: #D4AF37;
    }

    /* ===== 滚动条 ===== */
    QScrollBar:vertical {
        background: #F5DEB3;
        width: 8px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #D4AF37;
        border-radius: 4px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: #B8860B;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }

    /* ===== 滚动区域背景透明 ===== */
    QScrollArea {
        background-color: transparent;
        border: none;
    }
    """)