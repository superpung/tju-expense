#
# Created on Sun Dec 22 2024
#
# Copyright (c) 2024 Super Lee
#

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from rich.console import Console
from rich.table import Table


console = Console()


def analyze(df_file, title, save_to):
    """分析交易数据并生成可视化图表"""
    try:
        df = pd.read_csv(df_file)
    except pd.errors.EmptyDataError as e:
        console.log("没有数据")
        return None

    # 确保时间列为datetime类型
    df['time'] = pd.to_datetime(df['time'])

    plt.rcParams['font.sans-serif'] = ['LXGW WenKai Lite']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号
    plt.rcParams['font.size'] = 14  # 设置全局字体大小为14（可以根据需要调整）

    # 创建纵向图表布局 (3行2列的网格，但热力图和趋势图分别占一整行)
    fig = plt.figure(figsize=(12, 15))
    gs = plt.GridSpec(3, 3)

    # 1. 消费热力图 (第一行，跨越所有列)
    ax1 = fig.add_subplot(gs[0, :])
    plot_consumption_heatmap(df, ax1, title)

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
    return True

def plot_consumption_heatmap(df, ax, title):
    """绘制消费热力图"""
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
    cmap = sns.color_palette("Blues", as_cmap=True)

    # 绘制热力图
    sns.heatmap(
        daily_consumption,
        cmap=cmap,
        ax=ax,
        cbar_kws={'label': '消费金额', "orientation":"horizontal", "aspect": 50},
        fmt='.0f',
        square=True,  # 使用正方形格子
        linewidths=1,  # 添加网格线
        linecolor='white'  # 网格线颜色
    )

    # 设置标签
    ax.set_title(title, fontsize=24, pad=20)
    ax.set_ylabel('')
    ax.set_xlabel('')
    ax.set_yticklabels(['Mon', '', 'Wed', '', 'Fri', '', 'Sun'])

def plot_daily_trend(df, ax):
    """绘制每日消费趋势图"""
    # 计算每日消费总额
    daily_sum = df.groupby(df['time'].dt.date)['amount'].sum().reset_index()

    # 计算7日移动平均线
    daily_sum['MA7'] = daily_sum['amount'].rolling(
        window=7,
        min_periods=1  # 允许不足7天的数据也计算平均值
    ).mean()

    # 绘制折线图和移动平均线
    ax.plot(daily_sum['time'], daily_sum['amount'],
            '#a1c9f4', label='日消费')
    ax.plot(daily_sum['time'], daily_sum['MA7'],
            '#00468c', label='7日平均', linewidth=2)

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
    explode = [0] * len(type_stats)
    adjust_explode = [0, 0.02, 0.1, 0.15]
    explode = [adjust_explode[i] if i < len(adjust_explode) else _ for i, _ in enumerate(explode)]

    wedges, texts, autotexts = ax.pie(
        type_stats,
        labels=type_stats.index,
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.85,
        explode=explode,
        colors=sns.color_palette("pastel")
    )

    # 设置标题和样式
    ax.set_title('消费类型占比', pad=20)
    plt.setp(autotexts, size=8, weight="bold")
    plt.setp(texts, size=8)

def plot_place_statistics(df, ax):
    """绘制消费地点统计柱状图"""
    df = df[~df['type'].str.contains('水|电', na=False)]

    # 统计每个地点的消费总额并取前10
    place_stats = df.groupby('place')['amount'].sum()
    place_stats = place_stats.nlargest(10).sort_values(ascending=True)

    # 绘制横向柱状图
    bars = place_stats.plot(
        kind='barh',
        ax=ax,
        color='#a1c9f4'
    )

    # 设置标签
    ax.set_title('消费地点TOP10')
    ax.set_xlabel('消费金额')
    ax.set_ylabel('')

    # 在柱状图上添加数值标签
    for i, v in enumerate(place_stats):
        ax.text(v, i, f'{v:.2f}', va='center', fontsize=7)

def print_statistics(df_file):
    """打印基本统计信息"""
    try:
        df = pd.read_csv(df_file)
    except pd.errors.EmptyDataError as e:
        console.log("没有数据")
        return None

    df['time'] = pd.to_datetime(df['time'])

    # 创建表格
    table = Table(title="消费统计")

    # 添加列
    table.add_column("统计项", justify="left", style="cyan", no_wrap=True)
    table.add_column("数值", justify="right", style="magenta")

    # 添加行
    table.add_row("总消费金额", f"{df['amount'].sum():.2f}元")
    daily_average = df.groupby(df['time'].dt.date)['amount'].sum().mean()
    table.add_row("平均每日消费", f"{daily_average:.2f}元")
    table.add_row("平均每笔消费", f"{df['amount'].mean():.2f}元")
    table.add_row("消费笔数", f"{len(df)}笔")

    console.print(table, justify="center")

    # 消费类型统计
    type_stats = df.groupby('type')['amount'].agg(['count', 'sum', 'mean']).round(2)
    type_table = Table(title="消费类型统计")

    # 添加列
    type_table.add_column("类型", justify="left", style="cyan", no_wrap=True)
    type_table.add_column("笔数", justify="right", style="magenta")
    type_table.add_column("总金额", justify="right", style="magenta")
    type_table.add_column("平均金额", justify="right", style="magenta")

    # 添加行
    for index, row in type_stats.iterrows():
        type_table.add_row(index, str(row['count']), f"{row['sum']:.2f}元", f"{row['mean']:.2f}元")

    console.print(type_table, justify="center")

    # 每月消费统计
    monthly_stats = df.groupby(df['time'].dt.to_period('M'))['amount'].agg(['count', 'sum']).reset_index()
    monthly_stats['time'] = monthly_stats['time'].dt.to_timestamp()  # 转换为时间戳以便显示
    monthly_table = Table(title="每月消费统计")
    monthly_table.add_column("月份", justify="left", style="cyan", no_wrap=True)
    monthly_table.add_column("消费笔数", justify="right", style="magenta")
    monthly_table.add_column("总金额", justify="right", style="magenta")

    for index, row in monthly_stats.iterrows():
        monthly_table.add_row(f"{row['time'].month}月", str(row['count']), f"{row['sum']:.2f}元")

    console.print(monthly_table, justify="center")

    # 时段消费统计
    time_slots = {
        '早餐': (5, 11),  # 5点到11点
        '午餐': (11, 17),  # 11点到17点
        '晚餐': (17, 24)  # 17点到24点
    }

    time_slot_stats = {}
    filtered_df = df[~df['type'].str.contains('水|电', na=False)]
    for slot, (start, end) in time_slots.items():
        mask = (filtered_df['time'].dt.hour >= start) & (filtered_df['time'].dt.hour < end)
        time_slot_stats[slot] = filtered_df[mask]['amount'].agg(['count', 'sum'])

    time_slot_table = Table(title="时段消费统计")
    time_slot_table.add_column("时段", justify="left", style="cyan", no_wrap=True)
    time_slot_table.add_column("消费笔数", justify="right", style="magenta")
    time_slot_table.add_column("总金额", justify="right", style="magenta")
    time_slot_table.add_column("平均金额", justify="right", style="magenta")

    for slot, stats in time_slot_stats.items():
        avg_amount = stats['sum'] / stats['count'] if stats['count'] > 0 else 0
        time_slot_table.add_row(slot, str(stats['count']), f"{stats['sum']:.2f}元", f"{avg_amount:.2f}元")

    console.print(time_slot_table, justify="center")

    # 单笔消费
    max_transaction = df.loc[df['amount'].idxmax()]
    max_pos_transaction = filtered_df.loc[filtered_df['amount'].idxmax()]
    min_transaction = df.loc[df['amount'].idxmin()]
    min_pos_transaction = filtered_df.loc[filtered_df['amount'].idxmin()]
    earliest_transaction = df.loc[df['time'].idxmin()]
    latest_transaction = df.loc[df['time'].idxmax()]
    earliest_time_transaction = df.loc[df['time'].dt.time.idxmin()]
    latest_time_transaction = df.loc[df['time'].dt.time.idxmax()]
    earliest_time_pos_transaction = filtered_df.loc[filtered_df['time'].dt.time.idxmin()]
    latest_time_pos_transaction = filtered_df.loc[filtered_df['time'].dt.time.idxmax()]

    # 创建表格
    transaction_table = Table(title="单笔消费极值")
    transaction_table.add_column("类型", justify="left", style="cyan", no_wrap=True)
    transaction_table.add_column("金额", justify="right", style="magenta")
    transaction_table.add_column("时间", justify="left", style="magenta")
    transaction_table.add_column("地点", justify="left", style="magenta")

    # 添加行
    transaction_table.add_row("最大单笔消费", f"{max_transaction['amount']:.2f}元", str(max_transaction['time']), max_transaction['place'])
    transaction_table.add_row("最大食堂单笔消费", f"{max_pos_transaction['amount']:.2f}元", str(max_pos_transaction['time']), max_pos_transaction['place'])
    transaction_table.add_row("最小单笔消费", f"{min_transaction['amount']:.2f}元", str(min_transaction['time']), min_transaction['place'])
    transaction_table.add_row("最小食堂单笔消费", f"{min_pos_transaction['amount']:.2f}元", str(min_pos_transaction['time']), min_pos_transaction['place'])
    transaction_table.add_row("年度第一笔消费", f"{earliest_transaction['amount']:.2f}元", str(earliest_transaction['time']), earliest_transaction['place'])
    transaction_table.add_row("年度最后一笔消费", f"{latest_transaction['amount']:.2f}元", str(latest_transaction['time']), latest_transaction['place'])
    transaction_table.add_row("每日最早消费", f"{earliest_time_transaction['amount']:.2f}元", str(earliest_time_transaction['time']), earliest_time_transaction['place'])
    transaction_table.add_row("每日最晚消费", f"{latest_time_transaction['amount']:.2f}元", str(latest_time_transaction['time']), latest_time_transaction['place'])
    transaction_table.add_row("每日最早食堂消费", f"{earliest_time_pos_transaction['amount']:.2f}元", str(earliest_time_pos_transaction['time']), earliest_time_pos_transaction['place'])
    transaction_table.add_row("每日最晚食堂消费", f"{latest_time_pos_transaction['amount']:.2f}元", str(latest_time_pos_transaction['time']), latest_time_pos_transaction['place'])

    console.print(transaction_table, justify="center")

    return True
