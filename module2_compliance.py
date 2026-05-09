# 模块2代码
import os
import re
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLabel, QScrollArea, QFrame,
                             QFileDialog, QMessageBox, QListWidget, QListWidgetItem,
                             QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor, QDragEnterEvent, QDropEvent
from docx import Document
from PyPDF2 import PdfReader
from utils import AIWorker, Typewriter, COMPANY_LAW_PATH, MODULE2_MODEL
from zhipuai import ZhipuAI
from pdf_generator import generate_compliance_pdf

class ToastNotification(QFrame):
    """自定义轻提示，自动消失"""
    def __init__(self, parent, message, duration=3000, bg_color="#4CAF50"):
        super().__init__(parent)
        self.setObjectName("Toast")
        self.setStyleSheet(f"""
            #Toast {{
                background-color: {bg_color};
                border-radius: 8px;
                padding: 12px 20px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #1E293B; font-size: 13px; font-weight: 500;")
        layout.addWidget(label)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        if parent:
            parent_geo = parent.geometry()
            self.adjustSize()
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + parent_geo.height() - self.height() - 50
            self.move(x, y)

        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(200)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.start()

        QTimer.singleShot(duration, self.fade_out)

    def fade_out(self):
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(300)
        self.opacity_anim.setStartValue(1.0)
        self.opacity_anim.setEndValue(0.0)
        self.opacity_anim.finished.connect(self.deleteLater)
        self.opacity_anim.start()


class DragDropFrame(QFrame):
    """支持拖拽上传的文件区域"""
    def __init__(self, title, file_type_name, parent=None):
        super().__init__(parent)
        self.title = title
        self.file_type_name = file_type_name
        self.file_paths = []
        self.setAcceptDrops(True)
        self.setMinimumHeight(120)
        self.setMaximumHeight(180)
        self.setStyleSheet("""
            DragDropFrame {
                border: 2px dashed #CBD5E1;
                border-radius: 12px;
                background-color: #F8FAFC;
            }
            DragDropFrame:hover {
                border-color: #0F3460;
                background-color: #F0F4F8;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # 标题行
        title_layout = QHBoxLayout()
        icon_label = QLabel("" if "公司" in self.title else "📋")
        icon_label.setStyleSheet("font-size: 16px;")
        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-weight: bold; color: #16213E; font-size: 14px;")
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        self.browse_btn = QPushButton("浏览文件")
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 12px;
                color: #4A5568;
            }
            QPushButton:hover {
                background-color: #FFFFFF;
                border-color: #0F3460;
            }
        """)
        self.browse_btn.clicked.connect(self.browse_files)
        title_layout.addWidget(self.browse_btn)
        layout.addLayout(title_layout)

        # 提示文字
        hint_label = QLabel(f"拖拽{self.file_type_name}文件至此，或点击「浏览文件」")
        hint_label.setStyleSheet("color: #64748B; font-size: 12px;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint_label)

        # 文件列表（滚动区域）
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                border: none;
                background: transparent;
                font-size: 12px;
                color: #1E293B;
            }
            QListWidget::item {
                padding: 4px 0;
            }
            QListWidget::item:hover {
                background-color: #E6F0F3;
                border-radius: 4px;
            }
        """)
        self.file_list.setMaximumHeight(60)
        layout.addWidget(self.file_list)

    def browse_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, f"选择{self.file_type_name}文件", "",
            "文档文件 (*.docx *.txt *.md *.pdf);;所有文件 (*.*)"
        )
        if file_paths:
            self.add_files(file_paths)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                DragDropFrame {
                    border: 2px solid #1E5F74;
                    border-radius: 12px;
                    background-color: #E6F0F3;
                }
            """)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            DragDropFrame {
                border: 2px dashed #CBD5E1;
                border-radius: 12px;
                background-color: #F8FAFC;
            }
            DragDropFrame:hover {
                border-color: #0F3460;
                background-color: #F0F4F8;
            }
        """)
        event.accept()

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("""
            DragDropFrame {
                border: 2px dashed #CBD5E1;
                border-radius: 12px;
                background-color: #F8FAFC;
            }
            DragDropFrame:hover {
                border-color: #0F3460;
                background-color: #F0F4F8;
            }
        """)
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        self.add_files(files)
        event.acceptProposedAction()

    def add_files(self, file_paths):
        valid_exts = ('.docx', '.txt', '.md', '.pdf')
        new_files = []
        for fp in file_paths:
            ext = os.path.splitext(fp)[1].lower()
            if ext in valid_exts:
                if fp not in self.file_paths:
                    self.file_paths.append(fp)
                    self.file_list.addItem(f"✅ {os.path.basename(fp)}")
                    new_files.append(fp)
            else:
                self.file_list.addItem(f"❌ {os.path.basename(fp)} (格式不支持)")

        if new_files:
            # 通知外部
            if hasattr(self.parent(), 'on_files_added'):
                self.parent().on_files_added(self.file_type_name, new_files)

    def clear_files(self):
        self.file_paths.clear()
        self.file_list.clear()

    def get_file_paths(self):
        return self.file_paths.copy()


class Module2Interface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("data_interface")
        self.company_file_content = ""
        self.company_standard_content = ""
        self.law_content = ""
        self.loading_label = None
        self.result_label = None
        self.final_analysis_content = ""
        self.client = self._init_zhipu_client()
        self._load_company_law()
        self.init_ui()

    def _init_zhipu_client(self):
        try:
            client = ZhipuAI(api_key="")
            return client
        except Exception as e:
            print(f"AI客户端初始化失败：{e}")
            return None

    def _load_company_law(self):
        try:
            if not os.path.exists(COMPANY_LAW_PATH):
                self.law_content = "【错误】文件未找到"
                return
            doc = Document(COMPANY_LAW_PATH)
            law_text = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
            self.law_content = "\n".join(law_text)
        except Exception as e:
            self.law_content = f"【错误】加载失败：{str(e)}"

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        title_label = QLabel("📋 融资合规自查风险库")
        title_label.setStyleSheet("font-size:20px; font-weight:bold; color:#0F3460;")
        main_layout.addWidget(title_label)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color:#E2E8F0;")
        main_layout.addWidget(divider)

        drop_layout = QHBoxLayout()
        drop_layout.setSpacing(20)

        # 公司文件拖拽区
        self.company_drop = DragDropFrame("公司文件 (必填)", "公司文件")
        drop_layout.addWidget(self.company_drop)

        # 内部标准拖拽区
        self.standard_drop = DragDropFrame("内部标准 (可选)", "内部标准")
        drop_layout.addWidget(self.standard_drop)

        main_layout.addLayout(drop_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.analysis_btn = QPushButton("🔍 开始合规分析")
        self.analysis_btn.setMinimumHeight(40)
        self.analysis_btn.setStyleSheet("""
            QPushButton {
                background-color: #0F3460;
                border: none;
                border-radius: 8px;
                padding: 8px 28px;
                font-size: 14px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16213E;
            }
            QPushButton:pressed {
                background-color: #0A2847;
            }
        """)
        self.analysis_btn.clicked.connect(self.start_analysis)

        self.pdf_btn = QPushButton("导出PDF")
        self.pdf_btn.setMinimumHeight(40)
        self.pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid #CBD5E1;
                border-radius: 8px;
                padding: 8px 28px;
                font-size: 14px;
                color: #16213E;
                font-weight: 500;
            }
            QPushButton:hover {
                border-color: #0F3460;
                background-color: #F8FAFC;
            }
            QPushButton:disabled {
                border-color: #E8ECF0;
                color: #94A3B8;
            }
        """)
        self.pdf_btn.clicked.connect(self.export_to_pdf)
        self.pdf_btn.setEnabled(False)

        btn_layout.addWidget(self.analysis_btn)
        btn_layout.addWidget(self.pdf_btn)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)

        result_title = QLabel("分析结果：")
        result_title.setStyleSheet("font-size:16px; font-weight:bold; color:#0A2647; margin-top: 10px;")
        main_layout.addWidget(result_title)

        self.result_scroll = QScrollArea()
        self.result_scroll.setWidgetResizable(True)
        self.result_scroll.setStyleSheet("""
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    QScrollBar:vertical {
        border: none;
        background: #F1F5F9;
        width: 10px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background: #CBD5E1;
        border-radius: 5px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: #94A3B8;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
""")

    
        self.result_container = QWidget()
        self.result_container.setStyleSheet("background-color: #FFFFFF; border-radius: 8px;")
        self.result_layout = QVBoxLayout(self.result_container)
        self.result_layout.setContentsMargins(16, 16, 16, 16)
        self.result_layout.setSpacing(12)
        self.result_scroll.setWidget(self.result_container)
        main_layout.addWidget(self.result_scroll, 1)

        init_label = QLabel("请拖拽或点击上传公司文件（必填），可选内部标准文件，点击「开始合规分析」获取结果")
        init_label.setStyleSheet("font-size:14px; color:#64748B; padding:20px;")
        init_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_layout.addWidget(init_label)

    def on_files_added(self, file_type, new_files):
        """拖拽或浏览添加文件时的回调"""
        if file_type == "公司文件":
            self._process_company_files(new_files)
        else:
            self._process_standard_files(new_files)

    def _process_company_files(self, file_paths):
        self.company_file_content = ""
        success = 0
        for fp in file_paths:
            content = self._read_file(fp)
            if content is not None:
                self.company_file_content += f"\n=== 【文件：{os.path.basename(fp)}】 ===\n{content}"
                success += 1
        if success > 0:
            self._show_toast(f"成功读取 {success} 个公司文件", is_success=True)

    def _process_standard_files(self, file_paths):
        self.company_standard_content = ""
        success = 0
        for fp in file_paths:
            content = self._read_file(fp)
            if content is not None:
                self.company_standard_content += f"\n=== 【文件：{os.path.basename(fp)}】 ===\n{content}"
                success += 1
        if success > 0:
            self._show_toast(f"成功读取 {success} 个内部标准", is_success=True)

    def _read_file(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == ".docx":
                doc = Document(file_path)
                return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            elif ext == ".pdf":
                reader = PdfReader(file_path)
                return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            elif ext in [".txt", ".md"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception as e:
            self._show_toast(f"读取失败：{os.path.basename(file_path)}", is_success=False)
        return None

    def _show_toast(self, message, is_success=True):
        bg_color = "#10B981" if is_success else "#EF4444"
        toast = ToastNotification(self.window(), message, duration=2500, bg_color=bg_color)
        toast.show()

    def _clear_result(self):
        while self.result_layout.count() > 0:
            item = self.result_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _show_loading(self):
        self.loading_label = QLabel("AI正在进行合规分析，请稍候...")
        self.loading_label.setStyleSheet("font-size:14px; color:#165DFF; font-style:italic;")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._clear_result()
        self.result_layout.addWidget(self.loading_label)
        self.analysis_btn.setEnabled(False)

    def _hide_loading(self):
        if self.loading_label:
            self.loading_label.deleteLater()
            self.loading_label = None
        self.analysis_btn.setEnabled(True)

    def start_analysis(self):
        if not self.company_file_content:
            self._show_toast("请先上传需分析的公司文件", is_success=False)
            return
        if not self.client:
            self._show_toast("AI服务未连接", is_success=False)
            return
        self._show_loading()
        self._run_ai_analysis()

    def _run_ai_analysis(self):
        system_prompt = """
# 身份：企业融资合规自查分析师
你的核心任务是：
1. 基于《中华人民共和国商业银行法》《中华人民共和国证券法》《证券公司融资融券业务管理办法》三部法规全文（已提供）
2. 结合企业内部标准（如有提供则分析，无则忽略此维度）
3. 对企业上传的融资相关文件做**全维度合规自查与风险排查**

## 分析维度
1. 条款符合性：对比三部监管法规，指出不符合的具体内容
2. 风险等级：高/中/低（明确标注）
3. 整改建议：具体、可落地的整改措施
4. 内部标准冲突：仅当上传了企业标准时，才分析与监管法规的冲突点

## 输出格式（必须严格遵守）
【合规分析思路】
1. 分析范围：明确本次分析的融资文件内容和法律依据
2. 核心问题定位：找出关键违规/不合规点
3. 风险评估：基于监管法规条款评估风险等级

【合规问题清单】（每条必须严格按照以下格式，便于程序解析为表格）
问题描述：xxx | 违规条款：商业银行法/证券法/融资融券管理办法第x条 | 风险等级：x
问题描述：xxx | 违规条款：商业银行法/证券法/融资融券管理办法第x条 | 风险等级：x
...

【整改建议】
1. xxx
2. xxx

【补充说明】
- 如无合规问题则标注"未发现明显融资合规问题"
- 如未提供企业内部标准则标注"未上传企业内部标准，仅基于三部监管法规分析"
"""
        user_msg = f"""
        ## 分析材料
        1. 法规全文：{self.law_content[:5000]}
        2. 企业内部标准：{self.company_standard_content if self.company_standard_content else "未提供"}
        3. 企业文件：{self.company_file_content}
        """
        messages = [{"role":"system","content":system_prompt},{"role":"user","content":user_msg}]
        self.worker = AIWorker(self.client, messages, model=MODULE2_MODEL)
        self.worker.result_signal.connect(self._handle_analysis_result)
        self.worker.error_signal.connect(self._handle_analysis_error)
        self.worker.start()

    def _handle_analysis_result(self, data):
        self._hide_loading()
        thinking, answer = data
        self.final_analysis_content = f"【合规分析思路】\n{thinking}\n\n【最终分析结果】\n{answer}"
        self.pdf_btn.setEnabled(True)
        self._clear_result()
        self._display_analysis_result(thinking, answer)

    def _display_analysis_result(self, thinking, answer):
        # 1. 显示分析思路（纯文本）
        thinking_label = QLabel(f"【合规分析思路】\n{thinking}")
        thinking_label.setWordWrap(True)
        thinking_label.setStyleSheet("font-size:13px; color:#475569; background:#F8FAFC; padding:12px; border-radius:8px;")
        self.result_layout.addWidget(thinking_label)

        # 2. 解析问题清单并创建表格
        table = self._create_compliance_table(answer)
        if table is not None:
            self.result_layout.addWidget(table)

        # 3. 提取整改建议和补充说明（文本）
        other_text = self._extract_other_sections(answer)
        if other_text:
            other_label = QLabel(other_text)
            other_label.setWordWrap(True)
            other_label.setStyleSheet("font-size:13px; color:#1E293B; margin-top:8px;")
            self.result_layout.addWidget(other_label)

        if table is None and not other_text:
            raw_label = QLabel(answer)
            raw_label.setWordWrap(True)
            raw_label.setStyleSheet("font-size:13px; color:#1E293B;")
            self.result_layout.addWidget(raw_label)

    def _create_compliance_table(self, text):
        pattern = r"【合规问题清单】\s*(.*?)\s*(?:【整改建议】|【补充说明】|$)"
        match = re.search(pattern, text, re.DOTALL)
        if not match:
            return None

        content = match.group(1).strip()
        lines = content.split('\n')
        issues = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            clean_line = re.sub(r'^\d+\.\s*', '', line)
            if '|' in clean_line:
                issues.append(clean_line)

        if not issues:
            return None

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["问题描述", "违规条款", "风险等级"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E8ECF0;
                border-radius: 8px;
                background: #FFFFFF;
                gridline-color: #E8ECF0;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #E8ECF0;
            }
            QHeaderView::section {
                background-color: #F0F4F8;
                color: #0F3460;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #0F3460;
            }
            QTableWidget::item:selected {
                background-color: #E8F0F5;
            }
        """)

        row = 0
        for issue in issues:
            parts = issue.split('|')
            if len(parts) >= 3:
                desc = parts[0].replace('问题描述：', '').strip()
                clause = parts[1].replace('违规条款：', '').strip()
                risk = parts[2].replace('风险等级：', '').strip()

                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(desc))
                table.setItem(row, 1, QTableWidgetItem(clause))

                risk_item = QTableWidgetItem(risk)
                if '高' in risk:
                    risk_item.setForeground(QColor(0xD32F2F))
                elif '中' in risk:
                    risk_item.setForeground(QColor(0xF5A623))
                else:
                    risk_item.setForeground(QColor(0x2E7D32))
                table.setItem(row, 2, risk_item)
                row += 1

        if row == 0:
            return None

        for r in range(table.rowCount()):
            for c in range(table.columnCount()):
                item = table.item(r, c)
                if item:
                    item.setForeground(QColor(0x1E, 0x29, 0x3B))

        for i in range(row):
            table.setRowHeight(i, 50)
        return table

    def _extract_other_sections(self, text):
        text_without_issues = re.sub(r"【合规问题清单】.*?(?:【整改建议】|【补充说明】|$)", "", text, flags=re.DOTALL)
        sections = []
        for tag in ["【整改建议】", "【补充说明】"]:
            pattern = f"{tag}(.*?)(?=【|$)"
            match = re.search(pattern, text, re.DOTALL)
            if match:
                content = match.group(1).strip()
                if content:
                    sections.append(f"{tag}\n{content}")
        return "\n\n".join(sections) if sections else None

    def _handle_analysis_error(self, err):
        self._hide_loading()
        self._clear_result()
        error_label = QLabel(f"❌ 分析失败：{err}")
        error_label.setStyleSheet("font-size:14px; color:#EF4444;")
        self.result_layout.addWidget(error_label)

    def export_to_pdf(self):
        if not self.final_analysis_content:
            QMessageBox.warning(self, "提示", "暂无分析结果可导出！")
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "导出PDF报告", "自查风险库分析结果.pdf", "PDF文件 (*.pdf)")
        if save_path:
            if not save_path.endswith(".pdf"):
                save_path += ".pdf"
            try:
                generate_compliance_pdf(self.final_analysis_content, save_path)
                self._show_toast("PDF导出成功", is_success=True)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"PDF导出失败：{str(e)}")