#!/usr/bin/env python3
"""langchain 复现 Demo: 数据报表分析助手
功能: 读取 CSV → 自动统计 + 图表 + (可选) AI 解读
用法:
    python langchain_demo.py                      # 用内置示例数据
    python langchain_demo.py --csv 你的数据.csv    # 分析自己的数据
    python langchain_demo.py --ask "销量最高的3个区域?"  # AI问答(需API key)
"""
import argparse
import os
import sys

# ---------- 1. 数据层: 加载与统计 (不依赖 LLM, 立即可用) ----------
def load_and_stats(csv_path):
    import pandas as pd
    df = pd.read_csv(csv_path)
    stats = df.describe().round(2)
    return df, stats


def make_chart(df, out='analysis_chart.png'):
    """生成数据可视化图表 (seaborn)"""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import seaborn as sns

    # 中文字体: 优先用 Windows 微软雅黑 (WSL 可直接引用)
    from matplotlib import font_manager
    for fp in ['/mnt/c/Windows/Fonts/msyh.ttc', '/mnt/c/Windows/Fonts/msyhbd.ttc']:
        try:
            font_manager.fontManager.addfont(fp)
        except Exception:
            pass
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    num_cols = df.select_dtypes(include='number').columns.tolist()
    if not num_cols:
        print('⚠️ 没有数值列, 跳过图表')
        return None
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    # 左: 数值分布
    col = num_cols[0]
    sns.histplot(df[col].dropna(), kde=True, ax=axes[0])
    axes[0].set_title(f'{col} 分布')
    # 右: 数值列间关系 (取前两列)
    if len(num_cols) >= 2:
        sns.scatterplot(data=df, x=num_cols[0], y=num_cols[1], ax=axes[1])
        axes[1].set_title(f'{num_cols[0]} vs {num_cols[1]}')
    plt.tight_layout()
    plt.savefig(out, dpi=110)
    plt.close()
    return out


# ---------- 2. AI 层: langchain 智能分析 (需 API key) ----------
def ai_analysis(df, question=None):
    """用 LLM 解读数据。需要环境变量 DEEPSEEK_API_KEY。"""
    api_key = os.environ.get('DEEPSEEK_API_KEY') or os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return None

    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate

    # DeepSeek 兼容 OpenAI 接口
    llm = ChatOpenAI(
        model='deepseek-chat',
        api_key=api_key,
        base_url='https://api.deepseek.com/v1',
        temperature=0.3,
    )
    prompt = ChatPromptTemplate.from_messages([
        ('system', '你是一名资深数据分析师, 用简洁中文回答。'),
        ('human', '以下是数据摘要:\n{stats}\n\n问题: {question}'),
    ])
    chain = prompt | llm
    stats_text = df.describe().round(2).to_string()
    q = question or '请总结这些数据的关键发现与异常'
    return chain.invoke({'stats': stats_text, 'question': q}).content


# ---------- 3. 主流程 ----------
def main():
    ap = argparse.ArgumentParser(description='数据报表分析助手 (langchain demo)')
    ap.add_argument('--csv', help='CSV 文件路径 (默认内置示例数据)')
    ap.add_argument('--ask', help='向 AI 提问 (需 DEEPSEEK_API_KEY)')
    args = ap.parse_args()

    # 内置示例数据: 三个月销售记录
    if not args.csv:
        import tempfile
        import pandas as pd
        sample = pd.DataFrame({
            '月份': ['1月', '2月', '3月', '1月', '2月', '3月', '1月', '2月', '3月'],
            '区域': ['华东', '华东', '华东', '华南', '华南', '华南', '华北', '华北', '华北'],
            '销量': [320, 280, 350, 290, 310, 380, 210, 230, 260],
            '销售额': [12800, 11200, 14000, 11600, 12400, 15200, 8400, 9200, 10400],
        })
        tmp = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        sample.to_csv(tmp.name, index=False)
        csv_path = tmp.name
        print('📊 使用内置示例数据 (3区域 x 3月销售)')
    else:
        csv_path = args.csv

    print(f'\n📂 读取数据: {csv_path}')
    df, stats = load_and_stats(csv_path)
    print(f'   行数: {len(df)}, 列: {list(df.columns)}')
    print('\n📈 统计摘要:')
    print(stats)

    print('\n🖼️ 生成图表...')
    chart = make_chart(df)
    if chart:
        print(f'   ✅ 图表已保存: {chart}')

    print('\n🤖 AI 解读...')
    answer = ai_analysis(df, args.ask)
    if answer:
        print(f'   💡 {answer}')
    else:
        print('   ⚠️ 未配置 API key, 跳过 AI 解读 (见说明书配置 DEEPSEEK_API_KEY)')

    print('\n✅ 分析完成!')


if __name__ == '__main__':
    main()
