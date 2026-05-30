# 智能用户交互系统 —— 比赛作品 Demo

本项目是一个面向比赛设计的**智能用户交互系统**，集成了自然语言对话、合规性检测、情感评估与行为预测等核心功能。系统以 Python 编写，拥有图形化界面（基于 PyQt / Tkinter 等），并支持将对话与分析结果导出为 PDF 报告。

## 项目背景

本作品为某智能交互/人工智能类比赛的参赛 Demo，旨在展示一个具备多轮对话、风险监控、用户情感分析和未来行为预测能力的智能体框架。系统可应用于客服质检、心理辅导辅助、社区内容合规监控等场景。

## 主要功能

| 模块 | 功能说明 |
|------|----------|
| 💬 **智能聊天 (Module 1)** | 支持多轮自然语言交互，可进行上下文理解与回复生成。 |
| ✅ **合规性检查 (Module 2)** | 检测对话中是否包含敏感词、违规信息或高危言论，基于内置的风险词库。 |
| 📊 **用户评估 (Module 3)** | 对用户的情感倾向、对话质量或风险等级进行评估，输出量化指标。 |
| 🔮 **行为预测 (Module 4)** | 基于历史对话与情感特征，预测用户下一步可能的意图或行为。 |
| 📄 **PDF 报告生成** | 将完整的对话记录、分析结果及评估数据导出为 PDF 文件，便于存档或展示。 |
| 🖥️ **图形界面** | 提供登录窗口、主窗口和交互界面，支持鼠标与键盘操作，易于演示。 |

## 技术栈

- **语言**：Python 3.8+
- **GUI 框架**：PyQt5 / PySide2 (根据实际 `main_window.py` 推断)
- **依赖管理**：`requirements.txt`
- **情感分析**：基于自定义 `sentiment_dict.json` 词典规则或简单模型
- **PDF 生成**：通过 `pdf_generator.py` 调用 reportlab / fpdf 等库
- **打包工具**：`main.spec` 用于 PyInstaller 打包为独立可执行文件

## 项目结构
- Personal-demos/  
├── .vscode/ # VS Code 配置文件夹  
├── fonts/ # 界面所需字体文件  
├── resources/ # 图像、图标等资源  
├── pycache/ # Python 字节码缓存  
├── debug_data_load.py # 数据加载调试脚本  
├── home_page.py # 主页界面代码  
├── login_dialog.py # 登录对话框  
├── main.py # 程序主入口  
├── main.spec # PyInstaller 打包配置  
├── main_window.py # 主窗口核心逻辑  
├── module1_chat.py # 聊天模块  
├── module2_compliance.py # 合规检测模块  
├── module3_evaluation.py # 评估模块  
├── module4_prediction.py # 预测模块  
├── pdf_generator.py # PDF 生成器  
├── requirements.txt # Python 依赖列表  
├── sentiment_dict.json # 情感词典（用于评估）  
├── test.py # 单元测试脚本  
├── utils.py # 通用工具函数  
├── 智能体交互过程说明.md # 详细的交互流程说明（中文）  
└── 自查风险库分析结果.pdf # 示例风险库分析报告

## 安装与运行

### 1. 克隆仓库
```bash
git clone https://github.com/Residualcanliu/Personal-demos.git
cd Personal-demos
```

### 2. 安装依赖
建议使用虚拟环境：
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
# 或 venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 3. 运行程序
```bash
python main.py
```

### 4. 打包为可执行文件（可选）
```bash
pip install pyinstaller
pyinstaller main.spec
```
生成的可执行文件位于 dist/ 目录下。

## 使用说明
**登录**：启动后进入登录对话框，输入预设账号即可：  
```test
账号：admin  
密码：123456
```
**主界面**：左侧为对话历史，右侧为输入区和控制按钮。  
**执行分析**：发送消息后，系统会自动调用合规检测和情感评估。可手动点击“风险分析”“行为预测”等按钮获取详细报告。  
**生成报告**：点击“导出 PDF”可将当前对话及分析结果保存为 PDF 文件。  
情感词典 sentiment_dict.json 为基础词典，用户可根据需要扩充。  
合规检测词库内置于 module2_compliance.py 或外部文件中，如需修改请参考代码注释。  
**⚠注意**：本项目为比赛演示作品，未进行高并发或安全性加固，不建议直接部署至生产环境。

## 许可证
本项目仅作为个人学习与比赛展示使用，源代码不提供明确的开源许可证（All rights reserved），如有疑问请联系仓库所有者。

## 联系方式
- 作者：Residualcanliu
- Email：residualvmaple@gmail.com
- 项目地址：https://github.com/Residualcanliu/Personal-demos
