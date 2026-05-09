# 模块3代码
import os
import json
import numpy as np
from io import BytesIO
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QScrollArea, QFileDialog, QFrame,
                             QListWidget, QListWidgetItem, QSizePolicy, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage, QColor, QDragEnterEvent, QDropEvent
from docx import Document
from PyPDF2 import PdfReader
from utils import AIWorker, MODULE1_MODEL
from zhipuai import ZhipuAI
import matplotlib.pyplot as plt
from pdf_generator import generate_compliance_pdf

plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False


class ToastNotification(QFrame):
    """自定义轻提示，自动消失"""
    def __init__(self, parent, message, duration=2500, bg_color="#10B981"):
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


# 拖拽上传区域 
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
                border-color: #1E5F74;
                background-color: #F1F5F9;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        title_layout = QHBoxLayout()
        icon_label = QLabel("📂")
        icon_label.setStyleSheet("font-size: 16px;")
        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-weight: bold; color: #1E293B; font-size: 14px;")
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
                color: #475569;
            }
            QPushButton:hover {
                background-color: #FFFFFF;
                border-color: #1E5F74;
            }
        """)
        self.browse_btn.clicked.connect(self.browse_files)
        title_layout.addWidget(self.browse_btn)
        layout.addLayout(title_layout)

        hint_label = QLabel(f"拖拽{self.file_type_name}文件至此，或点击「浏览文件」")
        hint_label.setStyleSheet("color: #64748B; font-size: 12px;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint_label)

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
                border-color: #1E5F74;
                background-color: #F1F5F9;
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
                border-color: #1E5F74;
                background-color: #F1F5F9;
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
            if hasattr(self.parent(), 'on_files_added'):
                self.parent().on_files_added(self.file_type_name, new_files)

    def clear_files(self):
        self.file_paths.clear()
        self.file_list.clear()

    def get_file_paths(self):
        return self.file_paths.copy()


class Module3Interface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("analysis_interface")
        self.uploaded_file_content = ""
        self.client = self._init_zhipu_client()
        self.score_data = {}
        self.risk_list = []
        self.optimize_suggestions = []
        self.chart_pixmap = None
        self.init_ui()
        self._draw_empty_radar()

    def _init_zhipu_client(self):
        try:
            return ZhipuAI(api_key="")
        except Exception as e:
            print(f"AI客户端初始化失败：{e}")
            return None

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        title_label = QLabel("📊 企业融资能力智能评估系统")
        title_label.setStyleSheet("font-size:20px; font-weight:bold; color:#0F3460;")
        sub_title = QLabel("基于6大核心维度：企业规模、风险状况、经营质量、资本背景、成长性、知识产权")
        sub_title.setStyleSheet("font-size:13px; color:#64748B;")
        main_layout.addWidget(title_label)
        main_layout.addWidget(sub_title)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color:#E2E8F0;")
        main_layout.addWidget(divider)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 4)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)

        # 左上：上传区
        self.drop_frame = DragDropFrame("上传企业数据文件 (支持多选)", "企业数据")
        self.drop_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        grid_layout.addWidget(self.drop_frame, 0, 0)

        # 右上：按钮区
        right_top_widget = QWidget()
        right_top_layout = QVBoxLayout(right_top_widget)
        right_top_layout.setContentsMargins(0, 0, 0, 0)
        right_top_layout.setSpacing(10)
        right_top_layout.addStretch()

        self.analysis_btn = QPushButton("🔍 开始融资能力评估")
        self.analysis_btn.setMinimumHeight(36)
        self.analysis_btn.setMaximumWidth(220)
        self.analysis_btn.setStyleSheet("""
            QPushButton {
                background-color: #0F3460;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #16213E; }
            QPushButton:pressed { background-color: #0A2847; }
        """)
        self.analysis_btn.clicked.connect(self.start_evaluation)
        self.analysis_btn.setEnabled(False)
        right_top_layout.addWidget(self.analysis_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.export_chart_btn = QPushButton("💾 导出雷达图")
        self.export_chart_btn.setMinimumHeight(32)
        self.export_chart_btn.setMaximumWidth(220)
        self.export_chart_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 13px;
                color: #16213E;
                font-weight: 500;
            }
            QPushButton:hover {
                border-color: #0F3460;
                background-color: #F8FAFC;
            }
        """)
        self.export_chart_btn.clicked.connect(self.export_chart)
        self.export_chart_btn.setEnabled(False)
        right_top_layout.addWidget(self.export_chart_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.export_report_btn = QPushButton("📄 导出融资能力评估报告")
        self.export_report_btn.setMinimumHeight(36)
        self.export_report_btn.setMaximumWidth(220)
        self.export_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #0F3460;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #16213E; }
            QPushButton:pressed { background-color: #0A2847; }
        """)
        self.export_report_btn.clicked.connect(self.export_report)
        self.export_report_btn.setEnabled(False)
        right_top_layout.addWidget(self.export_report_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        right_top_layout.addStretch()
        grid_layout.addWidget(right_top_widget, 0, 1)

        # 左下：雷达图区
        left_bottom_widget = QWidget()
        left_bottom_layout = QVBoxLayout(left_bottom_widget)
        left_bottom_layout.setContentsMargins(0, 0, 0, 0)
        left_bottom_layout.setSpacing(8)

        chart_title = QLabel("📊 6大维度评分雷达图")
        chart_title.setStyleSheet("font-size:16px; font-weight:bold; color:#0F3460;")
        left_bottom_layout.addWidget(chart_title)

        self.chart_container = QFrame()
        self.chart_container.setStyleSheet("border:1px solid #E8ECF0; border-radius:8px; background:#FFFFFF;")
        self.chart_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        chart_container_layout = QVBoxLayout(self.chart_container)
        chart_container_layout.setContentsMargins(8, 8, 8, 8)

        self.chart_label = QLabel()
        self.chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.chart_label.setMinimumSize(280, 280)
        chart_container_layout.addWidget(self.chart_label)

        left_bottom_layout.addWidget(self.chart_container, 1)
        grid_layout.addWidget(left_bottom_widget, 1, 0)

        # 右下：评分结果区
        right_bottom_widget = QWidget()
        right_bottom_layout = QVBoxLayout(right_bottom_widget)
        right_bottom_layout.setContentsMargins(0, 0, 0, 0)
        right_bottom_layout.setSpacing(8)

        score_title = QLabel("📈 融资能力评分结果")
        score_title.setStyleSheet("font-size:16px; font-weight:bold; color:#0F3460;")
        right_bottom_layout.addWidget(score_title)

        self.score_scroll = QScrollArea()
        self.score_scroll.setWidgetResizable(True)
        self.score_scroll.setStyleSheet("border: none; background-color: transparent;")
        self.score_container = QWidget()
        self.score_container.setStyleSheet("background-color: #FFFFFF; border-radius: 8px;")
        self.score_layout = QVBoxLayout(self.score_container)
        self.score_layout.setContentsMargins(16, 16, 16, 16)
        self.score_layout.setSpacing(12)
        self.score_scroll.setWidget(self.score_container)
        right_bottom_layout.addWidget(self.score_scroll, 1)

        init_score_label = QLabel("请上传企业数据文件并点击「开始评估」获取结果")
        init_score_label.setStyleSheet("font-size:14px; color:#64748B; padding:20px;")
        init_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_layout.addWidget(init_score_label)

        grid_layout.addWidget(right_bottom_widget, 1, 1)

        main_layout.addLayout(grid_layout, 1)

    def on_files_added(self, file_type, new_files):
        self.uploaded_file_content = ""
        success = 0
        for fp in new_files:
            content = self._read_file(fp)
            if content is not None:
                self.uploaded_file_content += f"\n===== 文件：{os.path.basename(fp)} =====\n{content}\n\n"
                success += 1
        if success > 0:
            self._show_toast(f"成功读取 {success} 个文件", is_success=True)
            self.analysis_btn.setEnabled(True)
        else:
            self._show_toast("没有有效的文件被读取", is_success=False)

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
            print(f"读取失败：{e}")
        return None

    def _show_toast(self, message, is_success=True):
        bg_color = "#10B981" if is_success else "#EF4444"
        toast = ToastNotification(self.window(), message, duration=2500, bg_color=bg_color)
        toast.show()

    def _clear_result(self):
        while self.score_layout.count() > 0:
            item = self.score_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.score_data = {}
        self.risk_list = []
        self.optimize_suggestions = []
        self.export_chart_btn.setEnabled(False)
        self.export_report_btn.setEnabled(False)

    def _add_score_msg(self, text, is_success=False, is_error=False, is_loading=False, is_normal=True):
        label = QLabel(text)
        label.setWordWrap(True)
        if is_success:
            label.setStyleSheet("font-size:14px; color:#10B981;")
        elif is_error:
            label.setStyleSheet("font-size:14px; color:#EF4444;")
        elif is_loading:
            label.setStyleSheet("font-size:14px; color:#1E5F74; font-style:italic;")
        else:
            label.setStyleSheet("font-size:14px; color:#1E293B; line-height:1.6;")
        self.score_layout.addWidget(label)

    def _draw_empty_radar(self):
        labels = ["企业规模", "风险状况", "经营质量", "资本背景", "成长性", "知识产权"]
        scores = [0] * 6
        self.chart_pixmap = self._generate_radar_chart(
            labels, scores,
            figsize=(3.8, 3.8),
            label_fontsize=8,
            title_fontsize=10,
            dpi=100
        )
        self.chart_label.setPixmap(self.chart_pixmap)
        self.chart_label.setScaledContents(False)

    def _generate_radar_chart(self, labels, scores, figsize=(3.8, 3.8), label_fontsize=8, title_fontsize=10, dpi=100):
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        scores += scores[:1]
        angles += angles[:1]
        fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
        ax.plot(angles, scores, 'o-', linewidth=1.8, color='#0F3460')
        ax.fill(angles, scores, alpha=0.15, color='#0F3460')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=label_fontsize)
        ax.set_ylim(0, 10)
        ax.set_yticks(np.arange(0, 11, 2))
        ax.tick_params(axis='y', labelsize=7)
        ax.set_title("企业融资能力6大维度评分雷达图", fontsize=title_fontsize, pad=10, color='#0A2647')
        ax.grid(True, linestyle='--', alpha=0.4)
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        img = QImage.fromData(buf.getvalue())
        pixmap = QPixmap.fromImage(img)
        plt.close(fig)
        return pixmap

    def start_evaluation(self):
        if not self.uploaded_file_content:
            self._show_toast("请先上传企业数据文件", is_success=False)
            return
        if not self.client:
            self._show_toast("AI服务未连接", is_success=False)
            return
        self._clear_result()
        self._add_score_msg("AI正在综合分析...", is_loading=True)
        self.analysis_btn.setEnabled(False)
        self._run_ai_evaluation()

    def _run_ai_evaluation(self):
        system_prompt = """
        # 身份：企业融资能力专业评估师
        你的核心任务是基于企业上传的内部数据，按照6大核心维度完成融资能力评估：
        维度定义（满分均为10分）：
        1. 企业规模：注册资本、资产总额、员工数量、市场覆盖范围等
        2. 风险状况：债务率、现金流稳定性、合规风险、行业政策风险等
        3. 经营质量：营收增长率、利润率、资产周转率、客户复购率等
        4. 资本背景：股东背景、过往融资记录、战略合作资源等
        5. 成长性：市场增长率、产品迭代速度、行业天花板、扩张潜力等
        6. 知识产权：专利数量、商标、著作权、核心技术壁垒等

        ## 输出要求（必须严格遵守格式，先输出JSON再输出自然语言分析）
        ### JSON部分（用于程序解析，必须保证格式正确）
        {
            "total_score": 总分（60分制，各维度10分求和）,
            "dimension_scores": {
                "企业规模": 0-10分,
                "风险状况": 0-10分,
                "经营质量": 0-10分,
                "资本背景": 0-10分,
                "成长性": 0-10分,
                "知识产权": 0-10分
            },
            "risk_list": ["风险1", "风险2",...],
            "optimize_suggestions": ["建议1", "建议2",...]
        }

        ### 自然语言分析部分
        【融资能力总评】
        基于总分给出结论（如：优秀/良好/一般/较差/极差），说明企业整体融资可行性

        【6大维度细分分析】
        逐个维度分析得分原因、优势/不足

        【风险清单】
        1. 风险描述（对应risk_list）
        2....

        【优化建议】
        1. 具体可落地的优化措施（对应optimize_suggestions）
        2....

        ## 评估规则
        1. 评分客观，基于企业上传数据，无数据的维度标注0分并说明原因
        2. 风险清单需具体，避免空泛
        3. 优化建议需落地，贴合企业实际场景
        4. 总分≥50：优秀（融资成功率高）；40-49：良好；30-39：一般；20-29：较差；<20：极差
        """
        user_msg = f"## 企业上传多份数据文件（已合并）\n{self.uploaded_file_content}"
        messages = [{"role":"system","content":system_prompt},{"role":"user","content":user_msg}]
        self.worker = AIWorker(self.client, messages, model=MODULE1_MODEL)
        self.worker.result_signal.connect(self._handle_evaluation_result)
        self.worker.error_signal.connect(self._handle_evaluation_error)
        self.worker.start()

    def _parse_ai_result(self, ai_text):
        json_start = ai_text.find("{")
        json_end = ai_text.rfind("}") + 1
        json_str = ai_text[json_start:json_end]
        data = json.loads(json_str)
        natural_text = ai_text[json_end:].strip()
        return data, natural_text

    def _handle_evaluation_result(self, data):
        self.analysis_btn.setEnabled(True)
        thinking, answer = data
        try:
            score_data, natural_text = self._parse_ai_result(answer)
            self._clear_result()
            self.score_data = score_data
            self.risk_list = score_data["risk_list"]
            self.optimize_suggestions = score_data["optimize_suggestions"]
            full_result = f"""
【融资能力评估结果】
{natural_text}

【结构化评分数据】
总分（60分制）：{score_data['total_score']}分
维度细分得分：
- 企业规模：{score_data['dimension_scores']['企业规模']}分
- 风险状况：{score_data['dimension_scores']['风险状况']}分
- 经营质量：{score_data['dimension_scores']['经营质量']}分
- 资本背景：{score_data['dimension_scores']['资本背景']}分
- 成长性：{score_data['dimension_scores']['成长性']}分
- 知识产权：{score_data['dimension_scores']['知识产权']}分
"""
            self._add_score_msg(full_result)
            labels = list(score_data["dimension_scores"].keys())
            scores = list(score_data["dimension_scores"].values())
            self.chart_pixmap = self._generate_radar_chart(labels, scores)
            self.chart_label.setPixmap(self.chart_pixmap)
            self.chart_label.setScaledContents(False)
            self.export_chart_btn.setEnabled(True)
            self.export_report_btn.setEnabled(True)
        except Exception as e:
            self._add_score_msg(f"❌ 解析评估结果失败：{str(e)}", is_error=True)

    def _handle_evaluation_error(self, err):
        self._clear_result()
        self._add_score_msg(f"❌ 融资能力评估失败：{err}", is_error=True)
        self.analysis_btn.setEnabled(True)

    def export_chart(self):
        if not self.chart_pixmap:
            self._show_toast("暂无雷达图可导出！", is_success=False)
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "导出雷达图", "融资能力雷达图.png", "PNG图片 (*.png)")
        if save_path and self.chart_pixmap.save(save_path):
            self._show_toast("雷达图导出成功", is_success=True)

    def export_report(self):
        if not self.score_data:
            self._show_toast("暂无评估结果可导出！", is_success=False)
            return
        report_content = f"""
# 企业融资能力智能评估报告
## 一、评估总览
- 融资能力总分：{self.score_data['total_score']}分（60分制）
- 评估结论：{"优秀（融资成功率高）" if self.score_data['total_score']>=50 else "良好" if self.score_data['total_score']>=40 else "一般" if self.score_data['total_score']>=30 else "较差" if self.score_data['total_score']>=20 else "极差"}

## 二、6大维度细分得分
| 维度 | 得分（10分制） |
|------|----------------|
| 企业规模 | {self.score_data['dimension_scores']['企业规模']} |
| 风险状况 | {self.score_data['dimension_scores']['风险状况']} |
| 经营质量 | {self.score_data['dimension_scores']['经营质量']} |
| 资本背景 | {self.score_data['dimension_scores']['资本背景']} |
| 成长性 | {self.score_data['dimension_scores']['成长性']} |
| 知识产权 | {self.score_data['dimension_scores']['知识产权']} |

## 三、风险清单
{chr(10).join([f"{i+1}. {risk}" for i, risk in enumerate(self.risk_list)]) if self.risk_list else "未识别到明显风险"}

## 四、优化建议
{chr(10).join([f"{i+1}. {suggestion}" for i, suggestion in enumerate(self.optimize_suggestions)]) if self.optimize_suggestions else "暂无优化建议"}
"""
        save_path, _ = QFileDialog.getSaveFileName(self, "导出评估报告", "企业融资能力评估报告.pdf", "PDF文件 (*.pdf)")
        if save_path:
            if not save_path.endswith(".pdf"):
                save_path += ".pdf"
            try:
                generate_compliance_pdf(report_content, save_path)
                self._show_toast("报告导出成功", is_success=True)
            except Exception as e:
                self._show_toast(f"导出失败：{str(e)}", is_success=False)