# 模块1代码
import os
os.environ["AKSHARE_JS_ENGINE"] = "nodejs"
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTextEdit, QScrollArea, QListWidget,
                             QFileDialog, QMessageBox,QFrame)
from PyQt6.QtCore import Qt, QTimer
from docx import Document
from PyPDF2 import PdfReader
from utils import AIWorker, Typewriter, ZHIPU_API_KEY, MODULE1_MODEL
from zhipuai import ZhipuAI

class Module1Interface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chat_interface")
        self.conversations = {}
        self.current_id = None
        self.loading_label = None
        self.type_label = None
        self.uploaded_file_content = ""
        self.client = self._init_zhipu_client()
        self.init_ui()

    def _init_zhipu_client(self):
        try:
            client = ZhipuAI(api_key=ZHIPU_API_KEY)
            print("AI客户端初始化成功")
            return client
        except Exception as e:
            print(f"AI客户端初始化失败：{e}")
            return None

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setFixedWidth(200)
        left_widget.setStyleSheet("""
            background-color:#F0F4F8;
            border-right: 1px solid #E8ECF0;
        """)

        self.new_btn = QPushButton("新建对话")
        self.new_btn.clicked.connect(self.new_conversation)
        self.new_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                color: #16213E;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #F0F4F8;
            }
        """)
        left_layout.addWidget(self.new_btn)

        self.chat_list = QListWidget()
        self.chat_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                color: #4A5568;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #E8F0F5;
            }
            QListWidget::item:selected {
                background-color: #E8F0F5;
                color: #0F3460;
            }
        """)
        self.chat_list.itemClicked.connect(self.switch_conversation)
        left_layout.addWidget(self.chat_list)
    
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(24, 24, 24, 24)
        right_layout.setSpacing(0)

        # 聊天滚动区域（去除最外层边框）
        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setFrameShape(QFrame.Shape.NoFrame)          # 隐藏滚动区域的边框
        self.chat_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        # 聊天内容容器（白色背景，圆角，内边距）
        self.chat_content = QWidget()
        self.chat_content.setStyleSheet("background-color: #FFFFFF; border-radius: 16px;")
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(16)
        self.chat_layout.setContentsMargins(20, 20, 20, 20)
        self.chat_area.setWidget(self.chat_content)
        right_layout.addWidget(self.chat_area, stretch=1)

        # 固定空白区域（将输入区域下推）
        spacer = QWidget()
        spacer.setFixedHeight(40)
        spacer.setStyleSheet("background-color: transparent;")
        right_layout.addWidget(spacer, stretch=0)

        # 输入区域
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)

        # 文件上传行
        upload_layout = QHBoxLayout()
        self.upload_btn = QPushButton("📁 上传文件")
        self.upload_btn.clicked.connect(self.upload_file)
        self.file_label = QLabel("未选择文件")
        self.file_label.setStyleSheet("font-size:12px; color:#666;")
        upload_layout.addWidget(self.upload_btn)
        upload_layout.addWidget(self.file_label)
        upload_layout.addStretch()
        input_layout.addLayout(upload_layout)

        # 输入框行
        edit_layout = QHBoxLayout()
        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("输入分析指令...")
        self.input_edit.setMaximumHeight(100)
        self.send_btn = QPushButton("发送")
        self.send_btn.clicked.connect(self.send_message)
        edit_layout.addWidget(self.input_edit)
        edit_layout.addWidget(self.send_btn)
        input_layout.addLayout(edit_layout)

        right_layout.addWidget(input_container, stretch=0)

        # 组装主布局
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

        # 延迟新建第一个对话
        QTimer.singleShot(10, self.new_conversation)

    def add_msg(self, text, is_user):
        """添加带头像的气泡消息"""
        # 外层水平布局
        wrapper = QWidget()
        hbox = QHBoxLayout(wrapper)
        hbox.setContentsMargins(0, 8, 0, 8)
        hbox.setSpacing(12)

        # 头像标签
        avatar = QLabel()
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("""
            background-color: %s;
            border-radius: 18px;
            color: white;
            font-weight: bold;
            font-size: 16px;
        """ % ("#0F3460" if is_user else "#16213E"))
        avatar.setText("👤" if is_user else "🤖")

        # 气泡内容
        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        bubble.setStyleSheet("""
            QLabel {
                background-color: %s;
                color: %s;
                border-radius: 18px;
                padding: 12px 16px;
                font-size: 14px;
                border: %s;
            }
        """ % (
            "#DCF8C6" if is_user else "#F1F3F4",
            "#111111",
            "none" if is_user else "1px solid #E0E0E0"
        ))

        # 根据发送者排列顺序
        if is_user:
            hbox.addStretch()
            hbox.addWidget(bubble, alignment=Qt.AlignmentFlag.AlignRight)
            hbox.addWidget(avatar)
        else:
            hbox.addWidget(avatar)
            hbox.addWidget(bubble, alignment=Qt.AlignmentFlag.AlignLeft)
            hbox.addStretch()

        self.chat_layout.addWidget(wrapper)
        bubble.setMaximumWidth(int(self.chat_area.width() * 0.6))
        self.scroll_to_bottom()

    def new_conversation(self):
        chat_id = f"对话 {len(self.conversations)+1}"
        self.conversations[chat_id] = []
        self.chat_list.addItem(chat_id)
        self.current_id = chat_id
        self.clear_chat()
        self.uploaded_file_content = ""
        self.file_label.setText("未选择文件")
        self.chat_list.setCurrentRow(self.chat_list.count()-1)

        welcome_text = (
            "👋 您好！我是专业的融资融券数据智能体，可以为您提供：\n\n"
            "• 融资融券数据查询（融资余额、融券余量等）\n"
            "• 市场杠杆风险分析\n"
            "• 资金流向与机会洞察\n\n"
            "请告诉我您需要查询什么数据或分析什么标的？"
        )
        self.add_msg(welcome_text, is_user=False)
        self.conversations[chat_id].append({"content": welcome_text, "is_user": False})

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "文档文件 (*.docx *.pdf *.txt *.md);;所有文件 (*.*)"
        )
        if not file_path:
            return
        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_path)[1].lower()
        try:
            content = ""
            if ext == ".docx":
                doc = Document(file_path)
                for para in doc.paragraphs:
                    if para.text.strip():
                        content += para.text.strip() + "\n"
            elif ext == ".pdf":
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        content += text + "\n"
            elif ext in [".txt", ".md"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            else:
                raise Exception("不支持的文件格式")
            self.uploaded_file_content = content
            self.file_label.setText(f"已选择：{file_name}")
            self.add_msg(f"✅ 成功读取文件：{file_name}", False)
        except Exception as e:
            self.add_msg(f"❌ 文件读取失败：{str(e)}", False)
            self.uploaded_file_content = ""
            self.file_label.setText("读取失败")

    def switch_conversation(self, item):
        if not item:
            return
        self.current_id = item.text()
        self.clear_chat()
        self.uploaded_file_content = ""
        self.file_label.setText("未选择文件")
        for msg in self.conversations[self.current_id]:
            self.add_msg(msg["content"], msg["is_user"])

    def clear_chat(self):
        while self.chat_layout.count() > 0:
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def show_loading(self):
        self.loading_label = QLabel("AI正在深度思考中，请稍候...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.loading_label.setStyleSheet("font-size:14px; color:#666; font-style:italic;")
        self.chat_layout.addWidget(self.loading_label)
        self.scroll_to_bottom()

    def remove_loading(self):
        if self.loading_label:
            self.loading_label.deleteLater()
            self.loading_label = None

    def scroll_to_bottom(self):
        QTimer.singleShot(1, lambda: self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        ))

    def send_message(self):
        if not self.current_id:
            self.add_msg("❌ 对话未初始化，请点击「新建对话」", False)
            return
        user_prompt = self.input_edit.toPlainText().strip()
        if not user_prompt and not self.uploaded_file_content:
            self.add_msg("❌ 请输入指令或上传文件", False)
            return
        full_content = user_prompt
        if self.uploaded_file_content:
            full_content = f"用户指令：{user_prompt}\n\n参考文件内容：\n{self.uploaded_file_content}"
        display_msg = user_prompt if user_prompt else "【分析上传的文件】"
        self.add_msg(display_msg, True)
        self.conversations[self.current_id].append({"content": full_content, "is_user": True})
        self.input_edit.clear()
        self.uploaded_file_content = ""
        self.file_label.setText("未选择文件")
        if not self.client:
            self.add_msg("❌ AI服务未连接，无法分析", False)
            return
        self.show_loading()
        self.get_ai_response(full_content)

    def get_ai_response(self, user_msg):
        system_prompt = """
        你是专业的融资融券数据智能体，严格围绕【融资融券智能问数服务】和【杠杆风险/市场机会洞察】两大核心功能工作，禁止闲聊、偏离金融业务。

## 核心能力
1. 自然语言查数据：解析口语化指令，返回精准融资融券数据结果
2. 多轮对话澄清：需求模糊时主动提问确认
3. 核心指标查询：融资余额、融券余量、融资买入额、融券卖出量、资金流向等
4. 数据对比：交易日环比、跨标的对比、市场整体趋势对比
5. 风险洞察：识别杠杆风险、融资余额异常波动、融券做空激增、资金出逃风险
6. 机会挖掘：发现融资资金流入机会、热门标的趋势、市场情绪拐点、盈利潜力

## 工作规则
1. 基于用户上传的融资融券历史数据/对话上下文分析，无数据时引导上传
2. 回答简洁、专业、结构化（分点/短句）
3. 思考流程：需求解析→数据定位→计算/对比→风险/机会判断
4. 禁止编造金融数据，无数据时明确告知

## 输出格式
【🧠 AI 深度思考】
按步骤推理：解析用户需求 → 确认数据范围 → 执行查询/对比 → 识别风险/机会
【✅ 智能问数&洞察结果】
直接输出查询结果 + 数据结论 + 风险/机会提示
        """
        messages = [{"role": "system", "content": system_prompt}]
        for msg in self.conversations.get(self.current_id, []):
            role = "user" if msg["is_user"] else "assistant"
            messages.append({"role": role, "content": msg["content"]})
        self.worker = AIWorker(self.client, messages, model=MODULE1_MODEL)
        self.worker.result_signal.connect(self.show_typewriter)
        self.worker.error_signal.connect(self.show_error)
        self.worker.start()

    def show_typewriter(self, data):
        self.remove_loading()
        thinking, answer = data
        full_text = f"【🧠 AI 深度思考】\n{thinking}\n\n【✅ 最终分析结果】\n{answer}"

        # 创建气泡容器（与 add_msg 一致）
        bubble_wrapper = QWidget()
        wrapper_layout = QHBoxLayout(bubble_wrapper)
        wrapper_layout.setContentsMargins(0, 4, 0, 4)

        # 气泡标签
        self.type_label = QLabel("")
        self.type_label.setWordWrap(True)
        self.type_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.type_label.setObjectName("aiBubble")
        self.type_label.setStyleSheet("""
            #aiBubble {
                background-color: #F1F3F4;
                color: #111111;
                border-radius: 12px;
                padding: 10px 14px;
                font-size: 14px;
                border: 1px solid #E0E0E0;
            }
        """)

        wrapper_layout.addWidget(self.type_label, alignment=Qt.AlignmentFlag.AlignLeft)
        wrapper_layout.addStretch()

        self.chat_layout.addWidget(bubble_wrapper)
        self.type_label.setMaximumWidth(int(self.chat_area.width() * 0.7))

        # 打字机效果
        self.timer = Typewriter(full_text, 25)
        self.timer.update_text.connect(self.type_label.setText)
        self.timer.update_text.connect(self.scroll_to_bottom)
        self.timer.finished.connect(lambda: self.save_answer(full_text))
        self.timer.start()

    def save_answer(self, full_text):
        self.conversations[self.current_id].append({"content": full_text, "is_user": False})

    def show_error(self, err):
        self.remove_loading()
        self.add_msg(f"❌ 请求失败：{err}", False)