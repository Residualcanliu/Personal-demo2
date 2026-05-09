# 总控
import os
os.environ["AKSHARE_JS_ENGINE"] = "nodejs"
import sys
from PyQt6.QtCore import QThread, QTimer, pyqtSignal
from zhipuai import ZhipuAI

ZHIPU_API_KEY = ""
MODULE1_MODEL = "GLM-4-Plus"
MODULE2_MODEL = "glm-4"

PREDICT_DAYS = 7
OUTPUT_LIMIT = 20
THRESHOLD = 0.03

def get_resource_path(relative_path):
    """获取资源绝对路径，兼容打包后的临时目录"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 法规文件路径
COMPANY_LAW_PATH = get_resource_path("resources/中国商业银行法and证券法and证券公司融资融券业务管理办法.docx")
# 交易所数据文件映射
EXCHANGE_FILE_MAP = {
    "上交所": get_resource_path("resources/shanghai_data.csv"),
    "深交所": get_resource_path("resources/shenzhen_data.csv"),
    "北交所": get_resource_path("resources/beijing_data.csv")
}

class AIWorker(QThread):
    """AI请求工作线程"""
    result_signal = pyqtSignal(tuple)
    error_signal = pyqtSignal(str)

    def __init__(self, client, messages, model=MODULE1_MODEL, parent=None):
        super().__init__(parent)
        self.client = client
        self.messages = messages
        self.model = model

    def run(self):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                stream=False,
                extra_body={"enable_thinking": True}
            )
            thinking = getattr(response.choices[0].message, "thinking", "AI推理中...")
            answer = response.choices[0].message.content
            self.result_signal.emit((thinking, answer))
        except Exception as e:
            self.error_signal.emit(str(e))

class Typewriter(QTimer):
    """打字机逐字显示效果"""
    update_text = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, full_text, interval=25, parent=None):
        super().__init__(parent)
        self.full_text = full_text
        self.current_text = ""
        self.index = 0
        self.setInterval(interval)
        self.timeout.connect(self.type_next)

    def type_next(self):
        if self.index < len(self.full_text):
            self.current_text += self.full_text[self.index]
            self.update_text.emit(self.current_text)
            self.index += 1
        else:
            self.stop()
            self.finished.emit()