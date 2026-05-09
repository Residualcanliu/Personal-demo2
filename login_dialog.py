# 登录
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QWidget,
                             QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QIcon

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("登录 - 融智风控")
        self.setFixedSize(360, 280)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.drag_position = None
        self.init_ui()
        self.center()

    def init_ui(self):
        # 主容器（带圆角背景）
        main_widget = QWidget(self)
        main_widget.setObjectName("LoginWidget")
        main_widget.setStyleSheet("""
            #LoginWidget {
                background-color: #FFFFFF;
                border-radius: 16px;
                border: 1px solid #E8ECF0;
            }
            QLabel {
                color: #16213E;
                font-size: 13px;
            }
            QLineEdit {
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                color: #16213E;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border-color: #0F3460;
            }
            QPushButton {
                background-color: #0F3460;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16213E;
            }
            QPushButton:pressed {
                background-color: #0A2847;
            }
            QPushButton#cancelBtn {
                background-color: transparent;
                color: #64748B;
                border: 1px solid #CBD5E1;
            }
            QPushButton#cancelBtn:hover {
                background-color: #F0F4F8;
                color: #16213E;
            }
            QPushButton#closeBtn {
                background-color: transparent;
                color: #64748B;
                border: none;
                padding: 4px 8px;
                font-size: 16px;
                font-weight: normal;
            }
            QPushButton#closeBtn:hover {
                background-color: #FEE2E2;
                color: #B91C1C;
            }
        """)
        main_widget.setGeometry(0, 0, 360, 280)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题栏 
        title_bar = QWidget()
        title_bar.setFixedHeight(44)
        title_bar.setStyleSheet("background-color: transparent;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(16, 0, 8, 0)

        # 标题图标和文字
        title_icon = QLabel("🔐")
        title_icon.setStyleSheet("font-size: 14px;")
        title_layout.addWidget(title_icon)

        title_label = QLabel("融智风控 · 登录")
        title_label.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #0F3460;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 关闭按钮
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.reject)
        title_layout.addWidget(close_btn)

        layout.addWidget(title_bar)

        # 分割线
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #E8ECF0;")
        layout.addWidget(line)

        # 内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(32, 24, 32, 20)
        content_layout.setSpacing(16)

        # 用户名
        user_layout = QHBoxLayout()
        user_icon = QLabel("👤")
        user_icon.setFixedWidth(24)
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("用户名")
        user_layout.addWidget(user_icon)
        user_layout.addWidget(self.username_edit)
        content_layout.addLayout(user_layout)

        # 密码
        pass_layout = QHBoxLayout()
        pass_icon = QLabel("🔒")
        pass_icon.setFixedWidth(24)
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("密码")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        pass_layout.addWidget(pass_icon)
        pass_layout.addWidget(self.password_edit)
        content_layout.addLayout(pass_layout)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        self.login_btn = QPushButton("登 录")
        self.cancel_btn = QPushButton("取 消")
        self.cancel_btn.setObjectName("cancelBtn")
        self.login_btn.clicked.connect(self.check_login)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.login_btn)
        content_layout.addLayout(btn_layout)

        layout.addWidget(content_widget, 1)

        # 绑定回车键
        self.username_edit.returnPressed.connect(self.check_login)
        self.password_edit.returnPressed.connect(self.check_login)

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def check_login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        if username == "admin" and password == "123456":
            self.accept()
        else:
            QMessageBox.warning(self, "登录失败", "用户名或密码错误，请重试。")
            self.password_edit.clear()
            self.password_edit.setFocus()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()