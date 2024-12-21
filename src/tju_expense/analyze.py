import pandas as pd


def analyze(df_file):
    """分析交易数据"""
    df = pd.read_csv(df_file)
    print("\n=== 交易记录示例 ===")
    print(df.head())
    print("\n=== 交易数据分析 ===")
    print(f"总交易笔数: {len(df)}")
    print(f"\n交易类型统计:\n{df['type'].value_counts()}")
    print(f"\n总交易金额: {df['amount'].sum():.2f}")
    print(f"\n平均交易金额: {df['amount'].mean():.2f}")
    print(f"\n最大交易金额: {df['amount'].max():.2f}")
    print(f"\n最小交易金额: {df['amount'].min():.2f}")
