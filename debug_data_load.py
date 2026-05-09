import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# 获取资源绝对路径
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 调试三大证券所数据加载
def debug_data_load():
    # 存储每个交易所的近3天数据
    exchange_data = {}
    
    # 直接定义三大证券所的数据文件路径
    exchanges = [
        ("上交所", "resources/shanghai_data.csv"),
        ("深交所", "resources/shenzhen_data.csv"),
        ("北交所", "resources/beijing_data.csv")
    ]
    
    # 遍历三大证券所
    for exchange, relative_path in exchanges:
        # 获取绝对路径
        file_path = get_resource_path(relative_path)
        print(f"{exchange}文件路径: {file_path}")
        print(f"文件是否存在: {os.path.exists(file_path)}")
        
        if os.path.exists(file_path):
            try:
                print(f"开始加载{exchange}数据...")
                df = pd.read_csv(file_path)
                print(f"{exchange}数据行数: {len(df)}")
                print(f"{exchange}列名: {df.columns.tolist()}")
                
                # 标准化列名
                df.rename(columns={
                    "日期": "tradeDate",
                    "代码": "证券代码",
                    "名称": "证券简称",
                    "融资余额(元)": "融资余额(元)",
                    "本日融资余额(元)": "融资余额(元)"
                }, inplace=True)
                print(f"{exchange}重命名后列名: {df.columns.tolist()}")
                
                # 处理日期列
                if 'tradeDate' in df.columns:
                    print(f"{exchange}包含tradeDate列")
                    # 尝试多种日期格式解析
                    # 首先尝试 YYYY-MM-DD 格式
                    df['tradeDate'] = pd.to_datetime(df['tradeDate'], 
                                                    format='%Y-%m-%d', 
                                                    errors='coerce')
                    print(f"{exchange}初始日期解析后空值数量: {df['tradeDate'].isnull().sum()}")
                    
                    # 对于解析失败的行，尝试 YYYYMMDD 格式
                    mask = df['tradeDate'].isnull()
                    df.loc[mask, 'tradeDate'] = pd.to_datetime(df.loc[mask, 'tradeDate'], 
                                                               format='%Y%m%d', 
                                                               errors='coerce')
                    print(f"{exchange}最终日期解析后空值数量: {df['tradeDate'].isnull().sum()}")
                    
                    df = df.dropna(subset=['tradeDate'])
                    print(f"{exchange}过滤后数据行数: {len(df)}")
                    
                    # 按日期排序，取最近的3个交易日
                    df = df.sort_values('tradeDate', ascending=True)
                    unique_dates = df['tradeDate'].dt.date.unique()[-3:]
                    print(f"{exchange}最近3个交易日: {unique_dates}")
                    
                    # 存储该交易所的近3天数据
                    exchange_data[exchange] = []
                    for date in unique_dates:
                        day_data = df[df['tradeDate'].dt.date == date]
                        print(f"{exchange} {date}数据行数: {len(day_data)}")
                        
                        if not day_data.empty:
                            # 计算当日融资余额总量
                            total_balance = day_data['融资余额(元)'].sum() / 1e8  # 转换为亿元
                            print(f"{exchange} {date}融资余额: {total_balance:.2f} 亿元")
                            
                            # 计算涨跌幅（与前一天比较）
                            prev_date = date - timedelta(days=1)
                            prev_data = df[df['tradeDate'].dt.date == prev_date]
                            if not prev_data.empty:
                                prev_balance = prev_data['融资余额(元)'].sum() / 1e8
                                change_pct = ((total_balance - prev_balance) / prev_balance) * 100
                                change_str = f"{total_balance:.2f} 亿元，{change_pct:.2f}%"
                            else:
                                change_str = f"{total_balance:.2f} 亿元，N/A"
                            
                            exchange_data[exchange].append(change_str)
                            print(f"添加{exchange}数据: {change_str}")
            except Exception as e:
                print(f"加载{exchange}数据失败: {e}")
        else:
            print(f"{exchange}数据文件不存在: {file_path}")
    
    # 打印exchange_data
    print("\nexchange_data:", exchange_data)
    
    # 构建新闻列表
    all_news = []
    
    # 为每个交易所创建一行数据
    for exchange, data in exchange_data.items():
        # 确保有3天的数据
        while len(data) < 3:
            data.append("N/A")
        
        # 格式：交易所、前天、昨天、今天
        news_item = f"{exchange}、{data[0]}、{data[1]}、{data[2]}"
        all_news.append(news_item)
        print(f"添加新闻项: {news_item}")
    
    # 如果没有数据，添加提示
    if not all_news:
        all_news.append("暂无三大证券所数据")
    
    # 打印最终新闻列表
    print("\n最终新闻列表:", all_news)

if __name__ == "__main__":
    debug_data_load()