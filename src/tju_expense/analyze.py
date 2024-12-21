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
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号

    # 创建图表布局
    fig = plt.figure(figsize=(15, 10))

    # 1. 消费热力图 (2x2布局的第1个位置)
    ax1 = plt.subplot(2, 2, 1)
    plot_consumption_heatmap(df, ax1)

    # 2. 消费地点统计 (2x2布局的第2个位置)
    ax2 = plt.subplot(2, 2, 2)
    plot_place_statistics(df, ax2)

    # 3. 消费类型饼图 (2x2布局的第3个位置)
    ax3 = plt.subplot(2, 2, 3)
    plot_type_pie_chart(df, ax3)

    # 4. 每日消费趋势图 (2x2布局的第4个位置)
    ax4 = plt.subplot(2, 2, 4)
    plot_daily_trend(df, ax4)

    plt.tight_layout()
    plt.savefig(save_to, dpi=300, bbox_inches='tight')
    plt.close()

def plot_consumption_heatmap(df, ax):
    """绘制消费热力图"""
    # 准备数据
    df['day'] = df['time'].dt.day
    df['weekday'] = df['time'].dt.weekday

    # 计算每天的消费总额
    daily_consumption = df.pivot_table(
        values='amount',
        index='weekday',
        columns='day',
        aggfunc='sum'
    )

    # 绘制热力图
    sns.heatmap(
        daily_consumption,
        cmap='YlOrRd',
        ax=ax,
        cbar_kws={'label': '消费金额 (元)'},
        fmt='.1f'
    )

    # 设置标签
    ax.set_title('每日消费热力图')
    ax.set_ylabel('星期')
    ax.set_xlabel('日期')
    ax.set_yticklabels(['周一', '周二', '周三', '周四', '周五', '周六', '周日'])

def plot_place_statistics(df, ax):
    """绘制消费地点统计柱状图"""
    # 统计每个地点的消费总额
    place_stats = df.groupby('place')['amount'].sum().sort_values(ascending=True)

    # 绘制横向柱状图
    place_stats.plot(
        kind='barh',
        ax=ax,
        color='skyblue'
    )

    # 设置标签
    ax.set_title('消费地点统计')
    ax.set_xlabel('消费金额 (元)')
    ax.set_ylabel('消费地点')

    # 在柱状图上添加数值标签
    for i, v in enumerate(place_stats):
        ax.text(v, i, f'{v:.1f}元', va='center')

def plot_type_pie_chart(df, ax):
    """绘制消费类型饼图"""
    # 统计每种类型的消费总额
    type_stats = df.groupby('type')['amount'].sum()

    # 绘制饼图
    ax.pie(
        type_stats,
        labels=type_stats.index,
        autopct='%1.1f%%',
        startangle=90
    )

    ax.set_title('消费类型占比')

def plot_daily_trend(df, ax):
    """绘制每日消费趋势图"""
    # 计算每日消费总额
    daily_sum = df.groupby('time')['amount'].sum().reset_index()

    # 绘制折线图
    ax.plot(daily_sum['time'], daily_sum['amount'], marker='o')

    # 设置标签
    ax.set_title('每日消费趋势')
    ax.set_xlabel('日期')
    ax.set_ylabel('消费金额 (元)')

    # 旋转x轴日期标签
    plt.xticks(rotation=45)

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
