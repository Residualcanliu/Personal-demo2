# 主要展示主页的相关功能
import sys
import os
os.environ["AKSHARE_JS_ENGINE"] = "nodejs"
import json
import random
from datetime import datetime
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty, QMetaObject, Q_ARG
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.dates as mdates
from utils import EXCHANGE_FILE_MAP, ZHIPU_API_KEY, MODULE1_MODEL, AIWorker, get_resource_path
from zhipuai import ZhipuAI
import pandas as pd
from utils import get_resource_path


class ExchangeChartDialog(QDialog):
    """交易所历史数据折线图对话框"""
    def __init__(self, exchange_name, index_code, parent=None):
        super().__init__(parent)
        self.exchange_name = exchange_name
        self.index_code = index_code
        self.setWindowTitle(f"{exchange_name}历史数据")
        self.setMinimumSize(800, 600)
        
        # 布局
        main_layout = QVBoxLayout(self)
        
        # 时间粒度选择
        time_layout = QHBoxLayout()
        time_label = QLabel("时间粒度:")
        self.time_combo = QComboBox()
        self.time_combo.addItems(["日"])
        self.time_combo.currentIndexChanged.connect(self.update_chart)
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_combo)
        time_layout.addStretch()
        main_layout.addLayout(time_layout)
        
        # 图表区域
        self.figure = plt.figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas)
        
        # 实时更新复选框
        self.realtime_checkbox = QCheckBox("实时更新")
        self.realtime_checkbox.setChecked(False)
        self.realtime_checkbox.stateChanged.connect(self.toggle_realtime)
        main_layout.addWidget(self.realtime_checkbox)
        
        # 实时更新定时器
        self.realtime_timer = QTimer(self)
        self.realtime_timer.timeout.connect(self.update_chart)
        
        # 初始绘制图表
        self.update_chart()
    
    def toggle_realtime(self, state):
        """切换实时更新"""
        if state == Qt.CheckState.Checked.value:
            self.realtime_timer.start(60000)  # 每分钟更新一次
        else:
            self.realtime_timer.stop()
    
    def update_chart(self):
        """更新图表"""
        try:
            import akshare as ak
            from datetime import datetime, timedelta
            
            # 清除旧图表
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            # 获取时间粒度
            time_granularity = self.time_combo.currentText()
            
            # 根据时间粒度设置数据获取范围
            today = datetime.now()
            
            # 确保使用正确的指数代码
            if self.index_code == "bj899001":
                # 北交所使用示例股票代码
                stock_code = "831010"
            else:
                stock_code = self.index_code
            
            print(f"当前交易所: {self.exchange_name}")
            print(f"使用的代码: {stock_code}")
            print(f"时间粒度: {time_granularity}")
            
            if self.exchange_name == "北交所":
                print("北交所使用本地CSV文件数据...")
                csv_path = get_resource_path("resources/beijing_data.csv")
                try:
                    # 读取CSV文件
                    df = pd.read_csv(csv_path)
                    print(f"读取到的数据形状: {df.shape}")
                    print(f"数据列: {df.columns.tolist()}")
                    
                    # 检查数据是否为空
                    if not df.empty:
                        # 确保日期列存在
                        if '日期' in df.columns:
                            # 转换日期列
                            df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
                            # 过滤无效日期
                            df = df.dropna(subset=['日期'])
                            
                            # 按日期排序
                            df = df.sort_values('日期', ascending=True)
                            
                            # 设置日期为索引
                            df.set_index('日期', inplace=True)
                            
                            # 确保收盘价列存在
                            if '收盘价' in df.columns:
                                df = df.rename(columns={'收盘价': 'close'})
                            elif '指数' in df.columns:
                                df = df.rename(columns={'指数': 'close'})
                            
                            # 取最近30天的数据
                            df = df.tail(30)
                            print(f"处理后的数据形状: {df.shape}")
                            print(f"数据范围: {df.index[0]} 到 {df.index[-1]}")
                            print(f"最新数据日期: {df.index[-1]}")
                            
                            # 绘制折线图
                            ax.plot(df.index, df['close'], color='#D4AF37', linewidth=2)
                            ax.set_title(f"{self.exchange_name}近30日指数走势", fontsize=14)
                            ax.set_xlabel("日期", fontsize=12)
                            ax.set_ylabel("指数", fontsize=12)
                            
                            # 格式化x轴日期
                            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                            ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
                        else:
                            print("CSV文件中没有日期列，使用模拟数据...")
                            # 生成模拟数据
                            dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
                            base_index = 1000
                            import numpy as np
                            values = base_index + np.random.randn(30) * 50
                            df = pd.DataFrame({'close': values}, index=dates)
                            
                            # 绘制折线图
                            ax.plot(df.index, df['close'], color='#D4AF37', linewidth=2)
                            ax.set_title(f"{self.exchange_name}近30日指数走势", fontsize=14)
                            ax.set_xlabel("日期", fontsize=12)
                            ax.set_ylabel("指数", fontsize=12)
                            
                            # 格式化x轴日期
                            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                            ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
                    else:
                        print("CSV文件为空，使用模拟数据...")
                        # 生成模拟数据
                        dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
                        base_index = 1000
                        import numpy as np
                        values = base_index + np.random.randn(30) * 50
                        df = pd.DataFrame({'close': values}, index=dates)
                        
                        # 绘制折线图
                        ax.plot(df.index, df['close'], color='#D4AF37', linewidth=2)
                        ax.set_title(f"{self.exchange_name}近30日指数走势", fontsize=14)
                        ax.set_xlabel("日期", fontsize=12)
                        ax.set_ylabel("指数", fontsize=12)
                        
                        # 格式化x轴日期
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
                except Exception as e:
                    print(f"读取CSV文件失败: {e}")
                    # 生成模拟数据
                    dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
                    base_index = 1000
                    import numpy as np
                    values = base_index + np.random.randn(30) * 50
                    df = pd.DataFrame({'close': values}, index=dates)
                    
                    # 绘制折线图
                    ax.plot(df.index, df['close'], color='#D4AF37', linewidth=2)
                    ax.set_title(f"{self.exchange_name}近30日指数走势", fontsize=14)
                    ax.set_xlabel("日期", fontsize=12)
                    ax.set_ylabel("指数", fontsize=12)
                    
                    # 格式化x轴日期
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
            else:
                # 上交所和深交所使用AKShare数据
                print("使用stock_zh_index_daily获取日线数据...")
                try:
                    # 获取指数数据
                    df = ak.stock_zh_index_daily(symbol=stock_code)
                    print(f"获取到的数据形状: {df.shape}")
                    print(f"数据列: {df.columns.tolist()}")
                    
                    # 检查数据是否为空
                    if not df.empty:
                        # 确保索引是日期类型
                        if not pd.api.types.is_datetime64_any_dtype(df.index):
                            df.index = pd.to_datetime(df.index)
                        
                        # 按日期排序
                        df = df.sort_index(ascending=True)
                        
                        # 检查日期是否正确（排除1970年的错误日期）
                        valid_df = df[df.index > '1970-01-02']
                        if not valid_df.empty:
                            df = valid_df
                        else:
                            print("数据日期有问题，使用模拟数据...")
                            # 生成模拟数据
                            dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
                            # 为不同交易所生成不同的基础指数
                            if self.exchange_name == "上交所":
                                base_index = 4000
                            else:  # 深交所
                                base_index = 14500
                            
                            # 生成随机指数数据
                            import numpy as np
                            values = base_index + np.random.randn(30) * 50
                            df = pd.DataFrame({'close': values}, index=dates)
                        
                        # 取最近30天的数据
                        df = df.tail(30)
                        print(f"处理后的数据形状: {df.shape}")
                        print(f"数据范围: {df.index[0]} 到 {df.index[-1]}")
                        print(f"最新数据日期: {df.index[-1]}")
                        
                        # 检查数据是否为最新
                        today = pd.Timestamp.now().date()
                        latest_date = df.index[-1].date()
                        print(f"今天日期: {today}")
                        print(f"数据最新日期: {latest_date}")
                        
                        # 如果数据不是最新的，尝试使用其他接口
                        if (today - latest_date).days > 7:
                            print("数据不是最新的，尝试使用实时行情接口...")
                            try:
                                if self.exchange_name == "上交所":
                                    realtime_df = ak.stock_zh_a_spot()
                                    if not realtime_df.empty:
                                        # 找到上证指数
                                        sh_index = realtime_df[realtime_df['代码'] == 'sh000001']
                                        if not sh_index.empty:
                                            # 获取最新价格
                                            latest_price = sh_index.iloc[0]['最新价']
                                            # 添加今天的数据到DataFrame
                                            new_row = pd.DataFrame({'close': [latest_price]}, index=[pd.Timestamp.now().floor('D')])
                                            df = pd.concat([df, new_row])
                                            df = df.tail(30)
                                            print(f"添加了今天的实时数据 (上证指数): {latest_price}")
                            except Exception as e:
                                print(f"获取实时数据失败: {e}")
                                if self.exchange_name == "上交所":
                                    base_index = 4000
                                else:  # 深交所
                                    base_index = 14500
                                
                                # 生成今天的随机指数
                                import numpy as np
                                today_price = base_index + np.random.randn() * 50
                                new_row = pd.DataFrame({'close': [today_price]}, index=[pd.Timestamp.now().floor('D')])
                                df = pd.concat([df, new_row])
                                df = df.tail(30)
                                print(f"添加了今天的模拟数据: {today_price}")
                        
                        # 再次检查数据范围
                        if not df.empty:
                            print(f"最终数据范围: {df.index[0]} 到 {df.index[-1]}")
                        
                        # 绘制折线图
                        ax.plot(df.index, df['close'], color='#D4AF37', linewidth=2)
                        ax.set_title(f"{self.exchange_name}近30日指数走势", fontsize=14)
                        ax.set_xlabel("日期", fontsize=12)
                        ax.set_ylabel("指数", fontsize=12)
                        
                        # 格式化x轴日期
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
                    else:
                        # 数据为空，生成模拟数据
                        print("数据为空，生成模拟数据...")
                        dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
                        # 为不同交易所生成不同的基础指数
                        if self.exchange_name == "上交所":
                            base_index = 4000
                        else:  # 深交所
                            base_index = 14500
                        
                        # 生成随机指数数据
                        import numpy as np
                        values = base_index + np.random.randn(30) * 50
                        df = pd.DataFrame({'close': values}, index=dates)
                        
                        # 绘制折线图
                        ax.plot(df.index, df['close'], color='#D4AF37', linewidth=2)
                        ax.set_title(f"{self.exchange_name}近30日指数走势", fontsize=14)
                        ax.set_xlabel("日期", fontsize=12)
                        ax.set_ylabel("指数", fontsize=12)
                        
                        # 格式化x轴日期
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
                except Exception as e:
                    print(f"获取日线数据失败: {e}")
                    # 尝试使用股票数据作为备选
                    try:
                        print("尝试使用股票数据作为备选...")
                        stock_code = "600000" if self.exchange_name == "上交所" else "000001"
                        df = ak.stock_zh_a_daily(symbol=stock_code)
                        if not df.empty:
                            df = df.sort_index(ascending=True)
                            df = df.tail(30)
                            ax.plot(df.index, df['close'], color='#D4AF37', linewidth=2)
                            ax.set_title(f"{self.exchange_name}近30日指数走势", fontsize=14)
                            ax.set_xlabel("日期", fontsize=12)
                            ax.set_ylabel("指数", fontsize=12)
                        else:
                            ax.text(0.5, 0.5, "无数据可用", ha='center', va='center', transform=ax.transAxes)
                    except Exception as e2:
                        print(f"获取股票数据也失败: {e2}")
                        ax.text(0.5, 0.5, "数据加载失败", ha='center', va='center', transform=ax.transAxes)
            
            # 设置图表样式
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # 自动调整布局
            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            print(f"更新图表失败: {e}")
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, f"数据加载失败: {e}", ha='center', va='center', transform=ax.transAxes)
            self.canvas.draw()

class AnimatedCard(QFrame):
    """带动画的卡片，悬停时上浮并加深阴影"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._elevation = 0
        self.setGraphicsEffect(None)
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(10)
        self.shadow.setColor(QColor(0, 0, 0, 30))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
        self.setMouseTracking(True)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self:
            if event.type() == QEvent.Type.Enter:
                self.animate_elevation(1)
            elif event.type() == QEvent.Type.Leave:
                self.animate_elevation(0)
        return super().eventFilter(obj, event)

    def animate_elevation(self, target):
        self.anim = QPropertyAnimation(self, b"elevation")
        self.anim.setDuration(200)
        self.anim.setStartValue(self._elevation)
        self.anim.setEndValue(target)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

    @pyqtProperty(float)
    def elevation(self):
        return self._elevation

    @elevation.setter
    def elevation(self, value):
        self._elevation = value
        # 根据 elevation 调整阴影和位置
        blur = 10 + value * 8
        y_offset = 2 + value * 4
        color_alpha = 30 + value * 20
        self.shadow.setBlurRadius(blur)
        self.shadow.setOffset(0, y_offset)
        self.shadow.setColor(QColor(0, 0, 0, int(color_alpha)))
        # 轻微上移
        self.move(self.x(), self.y() + (1 if value > 0.5 else -1))

class HomePage(QWidget):
    navigate_to_module = pyqtSignal(int)
    update_news_signal = pyqtSignal(list)
    update_error_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.client = ZhipuAI(api_key=ZHIPU_API_KEY)
        # 定义三大证券所及其对应的指数代码
        self.exchanges = {
            "上交所": "sh000001",  # 上证指数
            "深交所": "sz399001",  # 深证成指
            "北交所": "bj899001"   # 北证50
        }
        self.init_ui()
        self.load_news()
        self.load_stock_rankings()

        # 连接信号
        self.update_news_signal.connect(self.update_news)
        self.update_error_signal.connect(self.show_error)

        # 连接列表项点击事件
        self.news_list.itemClicked.connect(self.on_news_item_clicked)

        self.news_timer = QTimer(self)
        self.news_timer.timeout.connect(self.load_news)
        self.start_daily_timer()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        self.banner = self.create_welcome_banner()
        main_layout.addWidget(self.banner)

        self.card_grid = QGridLayout()
        self.card_grid.setSpacing(20)

        self.news_card = self.create_news_card()
        self.market_card = self.create_market_card()
        self.stock_rank_card = self.create_stock_rank_card()   # 左上，小框

        self.card_grid.addWidget(self.stock_rank_card, 0, 0)  # 涨幅龙虎榜在左上小框
        self.card_grid.addWidget(self.market_card, 0, 1)  # 市场情绪温度计在右上
        self.card_grid.addWidget(self.news_card, 1, 0, 1, 2)  # 三大交易所数据在下方跨两列

        main_layout.addLayout(self.card_grid, 1)

    def create_welcome_banner(self):
        banner = QFrame()
        banner.setObjectName("WelcomeBanner")
        banner.setStyleSheet("""
#WelcomeBanner {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #D4AF37, stop:0.5 #FFD700, stop:1 #F5DEB3);
    border-radius: 24px;
    border: 1px solid #FFFFFF;
}
QLabel { color: #FFFFFF; background: transparent; border: none; }
""")
        banner.setFixedHeight(100)

        layout = QHBoxLayout(banner)
        layout.setContentsMargins(25, 10, 25, 10)

        text_layout = QVBoxLayout()
        title_label = QLabel("融智风控 · 企业融资智能决策系统")
        title_label.setStyleSheet("""
    font-size: 32px;
    font-weight: 900;
    color: #FFE4A1;
    font-family: "Microsoft YaHei", "SimHei", sans-serif;
""")
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(8)            # 阴影模糊半径
        shadow_effect.setColor(QColor(0, 0, 0, 180))  # 半透明黑色阴影
        shadow_effect.setOffset(2, 2)             # 阴影偏移量（右下）
        title_label.setGraphicsEffect(shadow_effect)
        self.slogan_label = QLabel("数据驱动决策，AI赋能融资")
        self.slogan_label.setStyleSheet("font-size: 13px; color: #F5EEDC;")
        text_layout.addWidget(title_label)
        text_layout.addWidget(self.slogan_label)
        layout.addLayout(text_layout)

        layout.addStretch()

        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.time_label.setStyleSheet("font-size: 14px;color:#FFFFFF;")
        self.update_time()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        layout.addWidget(self.time_label)
        return banner

    def update_time(self):
        now = datetime.now()
        date_str = now.strftime("%Y年%m月%d日")
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        weekday_str = weekdays[now.weekday()]
        time_str = now.strftime("%H:%M:%S")
        self.time_label.setText(f"{date_str} {weekday_str} {time_str}")

    def _create_card_base(self, title, icon="", is_clickable=True):
        card = AnimatedCard()  
        card.setObjectName("DashboardCard")
        card.setStyleSheet("""
#DashboardCard {
    background-color: #FFFDF5;
    border-radius: 16px;
    border: 1px solid #E8D5A3;
}
#DashboardCard:hover {
    border-color: #D4AF37;
}
QLabel#CardTitle {
    font-size: 16px;
    font-weight: bold;
    color: #333333;
}
""")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()
        title_label = QLabel(f"{icon} {title}")
        title_label.setObjectName("CardTitle")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        layout.addWidget(content_widget, 1)

        if is_clickable:
            more_link = QLabel("<a href='#' style='color: #D4AF37; text-decoration: none;'>查看更多 &gt;</a>")
            more_link.setAlignment(Qt.AlignmentFlag.AlignRight)
            more_link.setTextFormat(Qt.TextFormat.RichText)
            more_link.setOpenExternalLinks(False)
            layout.addWidget(more_link)

        return card, content_layout

    def create_news_card(self):
        card, layout = self._create_card_base("三大交易所数据", "📰")

        # 使用 QListWidget 展示新闻列表
        self.news_list = QListWidget()
        self.news_list.setStyleSheet("""
QListWidget {
    border: none;
    background: transparent;
    font-size: 14px;
    color: #333333;
}
QListWidget::item {
    padding: 12px 4px;
    border-bottom: 1px solid #F5DEB3;
}
QListWidget::item:hover {
    background-color: #FCF3DC;
    border-radius: 8px;
}
""")
        self.news_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(self.news_list, 1)

        # 初始占位
        self.news_list.addItem("AI正在为您生成今日快讯...")
        
        # 为卡片添加点击事件，但只有点击非列表区域时才跳转
        def card_clicked(event):
            # 检查点击位置是否在新闻列表上
            list_geo = self.news_list.geometry()
            if not list_geo.contains(event.pos()):
                self.navigate_to_module.emit(1)  # 跳转智能对话
        
        card.mousePressEvent = card_clicked
        return card

    def load_news(self):
        """从三大证券所数据文件中加载前3天数据"""
        self.news_list.clear()
        self.news_list.addItem("⏳ 正在加载三大证券所数据...")

        # 创建一个工作线程来处理数据加载
        class DataLoader(QObject):
            finished = pyqtSignal()
            
            def __init__(self, parent, callback):
                super().__init__(parent)
                self.callback = callback
            
            def run(self):
                self.callback()
                self.finished.emit()
        
        self.worker = DataLoader(None, self._load_exchange_data)
        self.thread = QThread(self)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def _load_exchange_data(self):
        """加载三大证券所的前3天数据"""
        import pandas as pd
        from datetime import datetime, timedelta
        
        try:
            # 存储每个交易所的近3天数据，格式为：[(余额, 涨跌幅), (余额, 涨跌幅), (余额, 涨跌幅)]
            exchange_data = {}
            
            # 定义三大证券所及其对应的指数代码
            exchanges = {
                "上交所": "sh000001",  # 上证指数
                "深交所": "sz399001",  # 深证成指
                "北交所": "bj899001"   # 北证50
            }

            try:
                import akshare as ak
                from datetime import datetime, timedelta
                
                # 获取当前日期
                today = datetime.now()
                # 计算10天前的日期，确保有足够的交易日数据
                start_date = (today - timedelta(days=10)).strftime("%Y%m%d")
                end_date = today.strftime("%Y%m%d")
                
                # 定义一个辅助函数来获取收盘价列名
                def get_close_column(df):
                    """获取DataFrame中的收盘价列名"""
                    possible_columns = ['close', '收盘', '最新价', 'CLOSE', '收盘价']
                    for col in possible_columns:
                        if col in df.columns:
                            return col
                    return None
                
                # 为每个交易所获取数据
                for exchange_name, index_code in exchanges.items():
                    try:
                        # 获取指数数据
                        print(f"使用akshare获取{exchange_name}数据...")
                        
                        if exchange_name == "北交所":
                            print(f"尝试使用stock_zh_a_hist_min_em获取北交所数据...")
                            # 使用北证50指数的股票代码
                            beijing_stock_code = "831010"  # 北证50指数成分股示例
                            df = ak.stock_zh_a_hist_min_em(symbol=beijing_stock_code, period="1", adjust="qfq")
                            
                            # 确保数据不为空
                            if not df.empty:
                                # 获取收盘价列名
                                close_col = get_close_column(df)
                                if close_col:
                                    # 取最新的收盘价作为今天的指数
                                    latest_close = df[close_col].iloc[-1]
                                    # 模拟昨天和前天的数据
                                    yesterday_close = latest_close * (1 - 0.005)
                                    day_before_yesterday_close = yesterday_close * (1 - 0.003)
                                    
                                    # 计算涨跌幅
                                    yesterday_change = ((yesterday_close - day_before_yesterday_close) / day_before_yesterday_close) * 100
                                    today_change = ((latest_close - yesterday_close) / yesterday_close) * 100
                                    
                                    # 构建数据
                                    data = [
                                        (f"{day_before_yesterday_close:.2f} 点", 0.0),  # 前天
                                        (f"{yesterday_close:.2f} 点", yesterday_change),  # 昨天
                                        (f"{latest_close:.2f} 点", today_change)  # 今天
                                    ]
                                    exchange_data[exchange_name] = data
                                    print(f"使用stock_zh_a_hist_min_em获取{exchange_name}数据成功")
                                else:
                                    # 找不到收盘价列，使用模拟数据
                                    print(f"无法找到收盘价列，使用模拟数据")
                                    base_index = 950
                                    today_index = base_index + 30 + random.uniform(-5, 5)
                                    yesterday_index = base_index + 20
                                    # 计算今天的涨跌幅
                                    today_change_pct = ((today_index - yesterday_index) / yesterday_index) * 100
                                    data = [
                                        (f"{base_index:.2f} 点", 0.0),  
                                        (f"{yesterday_index:.2f} 点", 0.5),  
                                        (f"{today_index:.2f} 点", today_change_pct)  
                                    ]
                                    exchange_data[exchange_name] = data
                                    print(f"使用模拟数据作为{exchange_name}数据")
                            else:
                                base_index = 950
                                today_index = base_index + 30 + random.uniform(-5, 5)
                                yesterday_index = base_index + 20
                                # 计算今天的涨跌幅
                                today_change_pct = ((today_index - yesterday_index) / yesterday_index) * 100
                                data = [
                                    (f"{base_index:.2f} 点", 0.0),  
                                    (f"{yesterday_index:.2f} 点", 0.5), 
                                    (f"{today_index:.2f} 点", today_change_pct)  
                                ]
                                exchange_data[exchange_name] = data
                                print(f"使用模拟数据作为{exchange_name}数据")
                        else:
                            df = ak.stock_zh_index_daily(symbol=index_code)
                            
                            # 确保数据不为空
                            if not df.empty:
                                # 按日期排序
                                df = df.sort_index(ascending=True)
                                
                                # 取最近的3个交易日
                                recent_data = df.tail(3)
                                
                                if len(recent_data) >= 3:
                                    data = []
                                    # 计算每天的涨跌幅
                                    for i in range(len(recent_data)):
                                        row = recent_data.iloc[i]
                                        # 获取收盘价
                                        close_col = get_close_column(recent_data)
                                        if close_col:
                                            close = row[close_col]
                                        else:
                                            if exchange_name == "上交所":
                                                base_index = 4000
                                            elif exchange_name == "深交所":
                                                base_index = 14500
                                            close = base_index + i * 10
                                        
                                        # 计算涨跌幅
                                        if i > 0:
                                            prev_row = recent_data.iloc[i-1]
                                            if close_col:
                                                prev_close = prev_row[close_col]
                                            else:
                                                prev_close = base_index + (i-1) * 10
                                            change_pct = ((close - prev_close) / prev_close) * 100
                                        else:
                                            change_pct = 0
                                        
                                        # 存储数据
                                        data.append((f"{close:.2f} 点", change_pct))
                                    
                                    # 更新数据
                                    exchange_data[exchange_name] = data
                                    print(f"使用akshare获取{exchange_name}数据成功")
                                else:
                                    if exchange_name == "上交所":
                                        base_index = 4000
                                    elif exchange_name == "深交所":
                                        base_index = 14500
                                    data = [
                                        (f"{base_index:.2f} 点", 0.0),  # 前天
                                        (f"{base_index + 20:.2f} 点", 0.5),  # 昨天
                                        (f"{base_index + 30:.2f} 点", 0.25)  # 今天
                                    ]
                                    exchange_data[exchange_name] = data
                            else:
                                if exchange_name == "上交所":
                                    base_index = 4000
                                elif exchange_name == "深交所":
                                    base_index = 14500
                             
                                data = [
                                    (f"{base_index:.2f} 点", 0.0),  # 前天
                                    (f"{base_index + 20:.2f} 点", 0.5),  # 昨天
                                    (f"{base_index + 30:.2f} 点", 0.25)  # 今天
                                ]
                                exchange_data[exchange_name] = data
                    except Exception as e:
                        print(f"使用akshare获取{exchange_name}数据失败: {e}")
        
                        if exchange_name == "上交所":
                            base_index = 4000
                        elif exchange_name == "深交所":
                            base_index = 14500
                        else:  # 北交所
                            base_index = 950
                    
                        today_index = base_index + 30 + random.uniform(-5, 5)
                        yesterday_index = base_index + 20
                        # 计算今天的涨跌幅
                        today_change_pct = ((today_index - yesterday_index) / yesterday_index) * 100
                        data = [
                            (f"{base_index:.2f} 点", 0.0),  # 前天
                            (f"{yesterday_index:.2f} 点", 0.5),  # 昨天
                            (f"{today_index:.2f} 点", today_change_pct)  # 今天
                        ]
                        exchange_data[exchange_name] = data
                        print(f"使用模拟数据作为{exchange_name}数据")
            except ImportError:
                print("akshare库未安装，使用模拟数据")

                for exchange_name in exchanges.keys():
                    if exchange_name == "上交所":
                        base_index = 4000
                    elif exchange_name == "深交所":
                        base_index = 14500
                    else:  # 北交所
                        base_index = 950
                    
                    today_index = base_index + 30 + random.uniform(-5, 5)
                    yesterday_index = base_index + 20
                    # 计算今天的涨跌幅
                    today_change_pct = ((today_index - yesterday_index) / yesterday_index) * 100
                    data = [
                        (f"{base_index:.2f} 点", 0.0),  # 前天
                        (f"{yesterday_index:.2f} 点", 0.5),  # 昨天
                        (f"{today_index:.2f} 点", today_change_pct)  # 今天
                    ]
                    exchange_data[exchange_name] = data
            
            # 构建新闻列表
            all_news = []
            
            # 为每个交易所创建一行数据
            for exchange_name, data in exchange_data.items():
                # 确保有3天的数据
                while len(data) < 3:
                    data.append(("N/A", 0))
                # 确保只有3天的数据
                data = data[:3]
                
                # 格式：交易所、(前天余额, 前天涨跌幅)、(昨天余额, 昨天涨跌幅)、(今天余额, 今天涨跌幅)
                all_news.append((exchange_name, data))
            
            # 使用信号在主线程中更新UI
            self.update_news_signal.emit(all_news)
        except Exception as e:
            print(f"加载数据失败: {e}")
            self.update_error_signal.emit(f"数据加载失败: {e}")

    def update_news(self, news_items):
        self.news_list.clear()
        print(f"接收到的news_items: {news_items}")
        
        try:
            mono_font = QFont("Consolas", 10)           
            header = "交易所      前日指数      涨跌幅    昨日指数      涨跌幅    今日指数      涨跌幅"
            header_item = QListWidgetItem(header)
            header_item.setForeground(QColor(0x0F, 0x34, 0x60))  # 深蓝色
            header_item.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
            self.news_list.addItem(header_item)
            
            # 显示新闻列表
            for item in news_items:
                if isinstance(item, tuple) and len(item) == 2:
                    exchange_name, data = item
                    # 确保有3天的数据
                    while len(data) < 3:
                        data.append(("N/A", 0))
                    # 确保只有3天的数据
                    data = data[:3]
                    
                    # 前天数据
                    balance1, change_pct1 = data[0]
                    if balance1 != "N/A":
                        if change_pct1 > 0:
                            change_str1 = f"+{change_pct1:.2f}%"
                        elif change_pct1 < 0:
                            change_str1 = f"{change_pct1:.2f}%"
                        else:
                            change_str1 = "0.00%"
                    else:
                        balance1 = "N/A"
                        change_str1 = "N/A"
                    
                    # 昨天数据
                    balance2, change_pct2 = data[1]
                    if balance2 != "N/A":
                        if change_pct2 > 0:
                            change_str2 = f"+{change_pct2:.2f}%"
                        elif change_pct2 < 0:
                            change_str2 = f"{change_pct2:.2f}%"
                        else:
                            change_str2 = "0.00%"
                    else:
                        balance2 = "N/A"
                        change_str2 = "N/A"
                    
                    # 今天数据
                    balance3, change_pct3 = data[2]
                    if balance3 != "N/A":
                        if change_pct3 > 0:
                            change_str3 = f"+{change_pct3:.2f}%"
                        elif change_pct3 < 0:
                            change_str3 = f"{change_pct3:.2f}%"
                        else:
                            change_str3 = "0.00%"
                    else:
                        balance3 = "N/A"
                        change_str3 = "N/A"
                    
                    # 使用等宽格式创建对齐的文本
                    text = f"{exchange_name:<10} {balance1:<16} {change_str1:<8} {balance2:<16} {change_str2:<8} {balance3:<16} {change_str3:<8}"
                    
                    # 创建列表项
                    list_item = QListWidgetItem(text)
                    list_item.setFont(mono_font)
                    
                    # 根据今天的涨跌幅度设置颜色
                    if balance3 != "N/A":
                        if change_pct3 > 0:
                            list_item.setForeground(QColor(0x2E, 0x7D, 0x32))  # 绿色
                        elif change_pct3 < 0:
                            list_item.setForeground(QColor(0xD3, 0x2F, 0x2F))  # 红色
                        else:
                            list_item.setForeground(QColor(0x16, 0x21, 0x3E))  # 深蓝色
                    else:
                        list_item.setForeground(QColor(0x16, 0x21, 0x3E))  # 深蓝色
                    
                    # 存储交易所信息，用于点击事件
                    list_item.setData(Qt.ItemDataRole.UserRole, (exchange_name, self.exchanges.get(exchange_name, "")))
                    
                    # 添加到列表
                    self.news_list.addItem(list_item)
                else:
                    # 处理旧格式的数据
                    self.news_list.addItem(str(item))
            print("三大证券所数据已更新")
        except Exception as e:
            print(f"更新新闻时出错: {e}")
            self.news_list.addItem(f"数据显示失败: {e}")

    def show_error(self, error_message):
        self.news_list.clear()
        self.news_list.addItem(error_message)

    def on_news_item_clicked(self, item):
        """处理新闻列表项点击事件"""
        # 获取存储的交易所信息
        exchange_info = item.data(Qt.ItemDataRole.UserRole)
        if exchange_info:
            exchange_name, index_code = exchange_info
            if exchange_name in self.exchanges:
                # 打开交易所历史数据对话框
                dialog = ExchangeChartDialog(exchange_name, index_code, self)
                dialog.exec()

    def start_daily_timer(self):
        # 立即加载一次数据
        self.load_news()
        # 设置定时器，每5分钟更新一次数据
        self.news_timer.start(5 * 60 * 1000)

    def create_market_card(self):
        card, layout = self._create_card_base("市场情绪温度计", "🌡️")
        card.mousePressEvent = lambda event: self.navigate_to_module.emit(4)  # 跳转涨跌预测

        self.market_figure = plt.figure(figsize=(5, 3), facecolor='#ffffff')
        self.market_canvas = FigureCanvas(self.market_figure)
        layout.addWidget(self.market_canvas, 1)
        self.plot_market_chart()
        return card

    def plot_market_chart(self):
        """从深交所真实数据绘制近30日全市场融资余额趋势"""
        import numpy as np
        self.market_figure.clear()
        ax = self.market_figure.add_subplot(111)

        try:
            file_path = EXCHANGE_FILE_MAP.get("深交所", "")
            if not os.path.exists(file_path):
                # 若深交所数据不存在，回退到上交所
                file_path = EXCHANGE_FILE_MAP.get("上交所", "")

            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                # 标准化列名
                df.rename(columns={
                    "日期": "tradeDate",
                    "代码": "证券代码",
                    "名称": "证券简称",
                    "融资余额(元)": "融资余额(元)"
                }, inplace=True)
                df['tradeDate'] = pd.to_datetime(df['tradeDate'], errors='coerce')
                df = df.dropna(subset=['tradeDate', '融资余额(元)'])

                # 按日期汇总全市场融资余额
                daily_balance = df.groupby('tradeDate')['融资余额(元)'].sum().reset_index()
                daily_balance = daily_balance.sort_values('tradeDate')

                # 取最近30个交易日
                daily_balance = daily_balance.tail(30)
                dates = daily_balance['tradeDate']
                balance = daily_balance['融资余额(元)'] / 1e8  # 转换为亿元

                ax.plot(dates, balance, color='#D4AF37', linewidth=2)
                ax.fill_between(dates, balance, min(balance), color='#D4AF37', alpha=0.1)
                ax.set_title("近30日全市场融资余额趋势", fontsize=12, pad=10)
                ax.set_xlabel("日期", fontsize=10)
                ax.set_ylabel("余额 (亿元)", fontsize=10)
                ax.grid(True, linestyle='--', alpha=0.6)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

                # 格式化x轴日期
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
                self.market_figure.autofmt_xdate()
            else:
                # 无数据时显示提示
                ax.text(0.5, 0.5, "暂无真实数据", ha='center', va='center', transform=ax.transAxes, fontsize=14, color='gray')
                ax.set_title("近30日全市场融资余额趋势", fontsize=12, pad=10)
        except Exception as e:
            print(f"加载真实数据失败：{e}")
            ax.text(0.5, 0.5, "数据加载失败", ha='center', va='center', transform=ax.transAxes, fontsize=14, color='gray')
            ax.set_title("近30日全市场融资余额趋势", fontsize=12, pad=10)

        self.market_figure.tight_layout()
        self.market_canvas.draw()

    def create_stock_rank_card(self):
        card, layout = self._create_card_base("涨跌龙虎榜", "📊")
        card.mousePressEvent = lambda event: self.navigate_to_module.emit(4)

        self.stock_tab = QTabWidget()
        self.stock_tab.setStyleSheet("""
    QTabWidget::pane { border: none; background: #FFFFFF; }
    QTabBar::tab {
        padding: 8px 20px; font-size:13px; color:#64748B;
        border:1px solid #D4AF37; border-bottom:none; border-radius:8px 8px 0 0;
    }
    QTabBar::tab:selected { color:#0F3460; font-weight:bold; background:#F9F2E7; }
""")
        # 上涨表格
        self.up_table = QTableWidget()
        self.up_table.setColumnCount(4)
        self.up_table.setHorizontalHeaderLabels(["代码", "名称", "连涨", "涨幅"])
        self.up_table.horizontalHeader().setStretchLastSection(True)   # 最后一列拉伸
        self.up_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.up_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.up_table.verticalHeader().setVisible(False)
        self.up_table.setStyleSheet("""
QTableWidget {
    border: none;
    background-color: #FFFDF5;
    gridline-color: #F5DEB3;
    font-size: 13px;
    color: #333333;
}
QTableWidget::item {
    padding: 10px 8px;
    border-bottom: 1px solid #F5DEB3;
}
""")
        # 设置各列宽度
        self.up_table.setColumnWidth(0, 80)   
        self.up_table.setColumnWidth(1, 160)  
        self.up_table.setColumnWidth(2, 60)   
        self.up_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        
        # 下跌表格
        self.down_table = QTableWidget()
        self.down_table.setColumnCount(4)
        self.down_table.setHorizontalHeaderLabels(["代码", "名称", "连跌", "跌幅"])
        self.down_table.horizontalHeader().setStretchLastSection(True)
        self.down_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.down_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.down_table.verticalHeader().setVisible(False)
        self.down_table.setStyleSheet("""
    QTableWidget { border:none; background:#FFFFFF; gridline-color:#F5EEDC; font-size:13px; }
    QTableWidget::item { padding:10px; border-bottom:1px solid #F5EEDC; }
""")
        self.down_table.setColumnWidth(0, 80)
        self.down_table.setColumnWidth(1, 160)
        self.down_table.setColumnWidth(2, 60)
        
        self.stock_tab.addTab(self.up_table, "📈 连续上涨")
        self.stock_tab.addTab(self.down_table, "📉 连续下跌")
        self.up_table.setAlternatingRowColors(False)
        self.down_table.setAlternatingRowColors(False)
        
        layout.addWidget(self.stock_tab, 1)
        return card

    def load_stock_rankings(self):
        up_data = [
            ("001325", "元创股份", "11", "17.18%"),
            ("603284", "林平发展", "10", "24.59%"),
            ("605089", "味知香", "10", "12.43%"),
            ("605566", "福莱蔥特", "10", "15.45%"),
            ("000703", "恒逸石化", "7", "30.43%"),
            ("002957", "科瑞技术", "7", "41.35%"),
            ("301055", "张小泉", "7", "40.96%"),
            ("301560", "众捷汽车", "7", "17.99%"),
        ]
        self.up_table.setRowCount(len(up_data))
        for row, (code, name, days, pct) in enumerate(up_data):
            self.up_table.setItem(row, 0, QTableWidgetItem(code))
            self.up_table.setItem(row, 1, QTableWidgetItem(name))
            self.up_table.setItem(row, 2, QTableWidgetItem(days))
            item = QTableWidgetItem(pct)
            item.setForeground(QColor(0xD3, 0x2F, 0x2F))   # 红色
            self.up_table.setItem(row, 3, item)

        down_data = [
            ("002222", "福晶科技", "6", "-28.00%"),
            ("600123", "兰花科创", "5", "-15.32%"),
            ("300456", "赛微电子", "4", "-12.11%"),
            ("688001", "华兴源创", "4", "-10.45%"),
            ("603019", "中科曙光", "3", "-8.90%"),
        ]
        self.down_table.setRowCount(len(down_data))
        for row, (code, name, days, pct) in enumerate(down_data):
            self.down_table.setItem(row, 0, QTableWidgetItem(code))
            self.down_table.setItem(row, 1, QTableWidgetItem(name))
            self.down_table.setItem(row, 2, QTableWidgetItem(days))
            item = QTableWidgetItem(pct)
            item.setForeground(QColor(0x2E, 0x7D, 0x32))  # 绿色
            self.down_table.setItem(row, 3, item)
        self.up_table.resizeColumnsToContents()
        self.down_table.resizeColumnsToContents()

    def create_quick_entry_card(self):
        card, layout = self._create_card_base("快捷功能", "⚡", is_clickable=False)
        # 创建网格布局
        grid = QGridLayout()
        grid.setSpacing(12)

        entries = [
            ("💬 智能对话", "AI助手", 1),
            ("📋 合规分析", "法规自查", 2),
            ("📊 融资评估", "能力评分", 3),
            ("📈 涨跌预测", "标的筛选", 4),
        ]

        for i, (title, desc, target_idx) in enumerate(entries):
            btn = QPushButton()
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F8FAFC;
                    border: 1px solid #E8ECF0;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: 500;
                    color: #16213E;
                }
                QPushButton:hover {
                    background-color: #E8F0F5;
                    border-color: #0F3460;
                }
            """)
            # 按钮内部布局
            vbox = QVBoxLayout(btn)
            vbox.setContentsMargins(10, 8, 10, 8)
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #0F3460;")
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet("font-size: 11px; color: #64748B;")
            vbox.addWidget(title_lbl)
            vbox.addWidget(desc_lbl)

            btn.clicked.connect(lambda checked, idx=target_idx: self.navigate_to_module.emit(idx))

            row = i // 2
            col = i % 2
            grid.addWidget(btn, row, col)

        layout.addLayout(grid, 1)
        return card