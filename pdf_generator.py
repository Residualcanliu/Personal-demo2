# 导出PDF功能代码
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListItem, ListFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re
import os
os.environ["AKSHARE_JS_ENGINE"] = "nodejs"
import sys


def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def init_pdf_fonts():
    """初始化内置字体，仅执行一次，避免重复注册报错"""
    simhei_path = get_resource_path("fonts/SIMHEI.ttf")
    simsun_path = get_resource_path("fonts/SIMSUN.ttc")
    
    if "SimHei" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("SimHei", simhei_path))
    if "SimSun" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("SimSun", simsun_path))

# 初始化字体
try:
    init_pdf_fonts()
except Exception as e:
    print(f"字体加载失败：{e}")


styles = getSampleStyleSheet()

# 大标题样式
title_style = ParagraphStyle(
    "ReportTitle",
    parent=styles["Heading1"],
    fontName="SimHei",
    fontSize=18,
    alignment=TA_CENTER,
    spaceAfter=20,
    textColor=colors.black
)

# 一级模块标题
section_style = ParagraphStyle(
    "SectionTitle",
    parent=styles["Heading2"],
    fontName="SimHei",
    fontSize=12,
    alignment=TA_LEFT,
    spaceBefore=15,
    spaceAfter=10,
    textColor=colors.black,
    fontWeight="bold"
)

# 正文样式
body_style = ParagraphStyle(
    "BodyText",
    parent=styles["Normal"],
    fontName="SimSun",
    fontSize=10,
    alignment=TA_LEFT,
    spaceAfter=5,
    leading=15 
)

# 有序列表项样式
ordered_list_style = ParagraphStyle(
    "OrderedListItem",
    parent=body_style,
    leftIndent=20,  
    spaceAfter=3
)

# 无序列表项样式
bullet_list_style = ParagraphStyle(
    "BulletListItem",
    parent=body_style,
    leftIndent=20,
    spaceAfter=3,
    bulletText="•" 
)

def filter_thinking_content(raw_content):
    """过滤深度思考部分，只保留【最终分析结果】后的内容"""
    result_match = re.search(r"【最终分析结果】\n(.*)", raw_content, re.DOTALL)
    if result_match:
        return result_match.group(1).strip()
    return re.sub(r"【合规分析思路】.*?【最终分析结果】", "", raw_content, flags=re.DOTALL).strip()

def parse_content_to_flow(content):
    flow = []
    flow.append(Paragraph("企业合规分析报告（公司法）", title_style))
    flow.append(Spacer(1, 10))

    sections = re.split(r"(【[^】]+】)", content)
    current_list = []

    for part in sections:
        part = part.strip()
        if not part:
            continue

        if part.startswith("【") and part.endswith("】"):
            if current_list:
                flow.append(ListFlowable(current_list, bulletType="1", leftIndent=20))
                current_list = []
            flow.append(Paragraph(part, section_style))
        else:
            lines = part.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if re.match(r"^\d+\. ", line):
                    list_text = re.sub(r"^\d+\. ", "", line)
                    current_list.append(ListItem(Paragraph(list_text, ordered_list_style)))

                elif line.startswith("- "):
                    bullet_text = line[2:].strip()
                    flow.append(Paragraph(f"• {bullet_text}", bullet_list_style))
                else:
                    flow.append(Paragraph(line, body_style))
    if current_list:
        flow.append(ListFlowable(current_list, bulletType="1", leftIndent=20))
    return flow

def generate_compliance_pdf(raw_ai_output, save_path):
    init_pdf_fonts()
    
    filtered_content = filter_thinking_content(raw_ai_output)
    if not filtered_content:
        filtered_content = "暂无合规分析结果"

    doc = SimpleDocTemplate(
        save_path,
        pagesize=A4,
        rightMargin=50, leftMargin=50,
        topMargin=50, bottomMargin=50
    )

    story = parse_content_to_flow(filtered_content)
    doc.build(story)
    print(f"✅ PDF已生成：{save_path}")

if __name__ == "__main__":
    test_content = """企业合规分析报告（公司法）
【合规分析思路】
1. 分析范围：本次分析对象为xx科技有限责任公司章程，依据《中华人民共和国公司法》全文进行合规性评估。
2. 核心问题定位：章程中存在多处与公司法强制性规定相冲突的条款，主要集中在股东权利、公司治理结构、出资方式、清算程序等方面。
3. 风险评估：基于公司法条款，该章程存在多处严重违反强制性规定的内容，可能导致章程部分或全部无效，公司治理结构混乱，股东权益受损，公司面临法律诉讼风险。
【最终分析结果】
【合规问题清单】
1. 问题描述：章程规定全体股东认缴出资无任何期限限制，永久无需实缴到位 | 违规条款：公司法第四十七条 | 风险等级：高
2. 问题描述：章程允许以个人劳务、个人信用作价出资，无需办理财产转移手续 | 违规条款：公司法第四十八条 | 风险等级：高
3. 问题描述：章程规定公司年度全部利润归大股东张三独自所有，小股东不享有分红权 | 违规条款：公司法第四十九条、第五十条 | 风险等级：高
4. 问题描述：章程规定仅大股东享有表决权，小股东无任何投票权 | 违规条款：公司法第四十二条、第四十三条 | 风险等级：高
5. 问题描述：章程规定股东不得对外转让股权，必须无偿转让给大股东 | 违规条款：公司法第八十二条、第八十三条 | 风险等级：高
6. 问题描述：章程规定不设立股东会、董事会、监事会，由大股东独自决定所有事项 | 违规条款：公司法第六十六条、第六十七条、第六十八条 | 风险等级：高
7. 问题描述：章程规定法定代表人可随意挪用公司资金、对外借款、处置公司资产 | 违规条款：公司法第十一条 | 风险等级：高
8. 问题描述：章程规定对外担保无需履行任何审批程序 | 违规条款：公司法第十五条 | 风险等级：高
9. 问题描述：章程规定清算后全部剩余财产归大股东所有，小股东无权分配 | 违规条款：公司法第二百二十六条 | 风险等级：高
10. 问题描述：章程规定与国家法律冲突时以章程约定为准 | 违规条款：公司法第五条 | 风险等级：高
【整改建议】
1. 修改注册资本条款，按照公司法规定明确出资期限，并在章程中注明股东应当在约定期限内实缴出资。
2. 修改出资方式条款，仅允许货币出资、实物出资、知识产权出资、土地使用权等公司法认可的出资方式，删除以个人劳务、个人信用作价出资的内容。
3. 修改利润分配条款，按照公司法规定，股东按照实缴的出资比例分取红利，公司章程另有规定的除外，但不得排除小股东的分红权。
4. 修改表决权条款，按照公司法规定，股东会会议由股东按照出资比例行使表决权，公司章程另有规定的除外，但不得完全排除小股东的表决权。
5. 修改股权转让条款，按照公司法规定，股东之间可以相互转让其全部或者部分股权；股东向股东以外的人转让股权，应当经其他股东过半数同意。
6. 修改组织机构条款，按照公司法规定设立股东会、董事会、监事会等必要的公司治理结构，明确各机构的职权和议事规则。
7. 修改法定代表人职权条款，明确法定代表人的职权范围，限制其随意挪用公司资金、处置公司资产等行为。
8. 修改对外担保条款，按照公司法规定，公司对外提供担保应当由董事会或者股东会决议，公司章程对担保总额及单项担保有限额规定的，不得超过限额。
9. 修改清算条款，按照公司法规定，公司财产在支付清算费用、职工工资、社会保险费用和法定补偿金，缴纳所欠税款，清偿公司债务后的剩余财产，有限责任公司按照股东的出资比例分配。
10. 删除章程中"与国家法律冲突时以章程约定为准"的条款，明确章程内容不得与法律、行政法规相冲突。
【补充说明】
- 未上传企业内部标准，仅基于公司法分析
- 该章程存在多处严重违反公司法强制性规定的内容，可能导致章程部分或全部无效，建议全面修订章程以确保合规性"""
    generate_compliance_pdf(test_content, "测试合规报告.pdf")