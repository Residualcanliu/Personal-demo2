from zhipuai import ZhipuAI
import uuid

# ===================== 配置区（仅修改这里） =====================
API_KEY = ""  # 填入你的密钥
USER_PROMPT = """
        基于以下本周市场热点，分析股票"腾讯"可能受到的影响：
        用户未来计划：无
        基于当前市场情绪指数
        请用一段话简要说明主要热点对该股票的情感影响，并给出短期和长期展望。
        """
MODEL = "glm-4-plus"             # 固定模型
# ===============================================================

# 初始化客户端
client = ZhipuAI(api_key=API_KEY)

# 调用GLM-4-Plus获取回复
response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": USER_PROMPT}]
)
ai_reply = response.choices[0].message.content

# ===================== 生成比赛要求的格式 =====================
result = {
    "id": str(uuid.uuid4()),  # 自动生成唯一ID
    "messages": [
        {
            "role": "user",
            "content": USER_PROMPT
        },
        {
            "role": "assistant",
            "content": ai_reply
        }
    ]
}

# 1. 控制台打印（标准格式）
print("id:", result["id"], ",\n")
print("messages: [")
for msg in result["messages"]:
    print(f"{{\nrole: {msg['role']},\ncontent: {msg['content']}\n}},")
print("]")

