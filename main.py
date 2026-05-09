# 主函数，Root_Enter用于开发，可以跳过登录
# Admin_Enter需要输入账号密码，账号：admin 密码：123456
# pip install nodejs-bin    
import sys
import subprocess
from PyQt6.QtWidgets import QApplication
from login_dialog import LoginDialog
from main_window import MainWindow

def Root_Enter():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

def Admin_Enter():
    try:
        app = QApplication(sys.argv)
        login = LoginDialog()
        if login.exec() == LoginDialog.DialogCode.Accepted:
            window = MainWindow()
            window.show()
            sys.exit(app.exec())
        else:
            sys.exit(0) 
    except Exception as e:
        print(f"程序崩溃: {e}")
        sys.exit(1)
if __name__ == "__main__":
    Root_Enter()
    # Admin_Enter()
    