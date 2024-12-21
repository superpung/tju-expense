import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import calendar
import numpy as np


def analyze(df_file, save_to):
    """分析交易数据并生成可视化图表"""
    df = pd.read_csv(df_file)
    # 确保时间列为datetime类型
    df['time'] = pd.to_datetime(df['time'])

    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号

    # 创建纵向图表布局 (3行2列的网格，但热力图和趋势图分别占一整行)
    fig = plt.figure(figsize=(12, 15))
    gs = plt.GridSpec(3, 3, height_ratios=[1.2, 1, 1])

    # 1. 消费热力图 (第一行，跨越所有列)
    ax1 = fig.add_subplot(gs[0, :])
    plot_consumption_heatmap(df, ax1)

    # 2. 每日消费趋势图 (第二行，跨越所有列)
    ax2 = fig.add_subplot(gs[1, :])
    plot_daily_trend(df, ax2)

    # 3. 消费类型饼图 (第三行，第一列)
    ax3 = fig.add_subplot(gs[2, 0])
    plot_type_pie_chart(df, ax3)

    # 4. 消费地点统计 (第三行，第二列)
    ax4 = fig.add_subplot(gs[2, 1:])
    plot_place_statistics(df, ax4)

    plt.tight_layout()
    plt.savefig(save_to, dpi=300, bbox_inches='tight')
    plt.close()

def plot_consumption_heatmap(df, ax):
    """绘制类似GitHub contribution的消费热力图"""
    # 准备数据
    df['weekday'] = df['time'].dt.weekday
    df['week'] = df['time'].dt.isocalendar().week

    # 计算每天的消费总额
    daily_consumption = df.pivot_table(
        values='amount',
        index='weekday',
        columns='week',
        aggfunc='sum',
        fill_value=0
    )

    # 设置颜色映射
    cmap = sns.color_palette("YlOrRd", as_cmap=True)

    # 绘制热力图
    sns.heatmap(
        daily_consumption,
        cmap=cmap,
        ax=ax,
        cbar_kws={'label': '消费金额 (元)', "orientation":"horizontal", "aspect": 50},
        fmt='.0f',
        square=True,  # 使用正方形格子
        linewidths=1,  # 添加网格线
        linecolor='white'  # 网格线颜色
    )

    # 设置标签
    ax.set_title('消费热力图', pad=20)
    ax.set_ylabel('')
    ax.set_xlabel('')
    ax.set_yticklabels(['Mon', '', 'Wed', '', 'Fri', '', 'Sun'])

def plot_daily_trend(df, ax):
    """绘制每日消费趋势图"""
    # 计算每日消费总额
    daily_sum = df.groupby('time')['amount'].sum().reset_index()

    # 计算7日移动平均线
    daily_sum['MA7'] = daily_sum['amount'].rolling(
        window=7,
        min_periods=1  # 允许不足7天的数据也计算平均值
    ).mean()

    # 绘制折线图和移动平均线
    ax.plot(daily_sum['time'], daily_sum['amount'],
            alpha=0.6, label='日消费')
    ax.plot(daily_sum['time'], daily_sum['MA7'],
            'r-', label='7日移动平均', linewidth=2)

    # 设置标签
    ax.set_title('每日消费趋势')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.legend()

    # 旋转x轴日期标签
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

def plot_type_pie_chart(df, ax):
    """绘制消费类型饼图"""
    # 统计每种类型的消费总额
    type_stats = df.groupby('type')['amount'].sum()

    # 计算百分比
    total = type_stats.sum()
    type_pcts = type_stats / total * 100

    # 绘制饼图
    wedges, texts, autotexts = ax.pie(
        type_stats,
        labels=type_stats.index,
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.85
    )

    # 设置标题和样式
    ax.set_title('消费类型占比')
    plt.setp(autotexts, size=8, weight="bold")
    plt.setp(texts, size=8)

def plot_place_statistics(df, ax):
    """绘制消费地点统计柱状图"""
    # 统计每个地点的消费总额并取前10
    place_stats = df.groupby('place')['amount'].sum()
    place_stats = place_stats.nlargest(10).sort_values(ascending=True)

    # 绘制横向柱状图
    bars = place_stats.plot(
        kind='barh',
        ax=ax,
        color='skyblue'
    )

    # 设置标签
    ax.set_title('消费地点TOP10')
    ax.set_xlabel('消费金额')
    ax.set_ylabel('')

    # 在柱状图上添加数值标签
    for i, v in enumerate(place_stats):
        ax.text(v, i, f'{v:.0f}', va='center')

    # 调整字体大小
    ax.tick_params(axis='y', labelsize=8)

def print_statistics(df):
    """打印基本统计信息"""
    print("\n=== 消费统计分析 ===")
    print(f"总消费金额: {df['amount'].sum():.2f}元")
    print(f"平均每日消费: {df['amount'].mean():.2f}元")
    print(f"最大单笔消费: {df['amount'].max():.2f}元")
    print(f"消费笔数: {len(df)}笔")

    print("\n消费类型统计:")
    print(df.groupby('type')['amount'].agg(['count', 'sum', 'mean']).round(2))

    print("\n消费地点TOP5:")
    print(df.groupby('place')['amount'].sum().sort_values(ascending=False).head())
