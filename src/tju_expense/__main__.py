import os
import sys
import argparse
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

from .analyze import analyze
from .fetch import Fetcher


def get_args():
    """获取命令行参数，包括Cookie值和日期范围"""
    parser = argparse.ArgumentParser(description='获取并分析交易数据')
    parser.add_argument('--cookie', help='登录Cookie')
    parser.add_argument('--start', help='开始日期', default='2022-12-01')
    parser.add_argument('--end', help='结束日期', default='2022-12-31')
    args = parser.parse_args()

    if not args.cookie:
        load_dotenv()
        args.cookie = os.getenv('COOKIE')

    if not args.cookie:
        print("请输入登录Cookie值：")
        args.cookie = input().strip()
        if not args.cookie:
            print("错误：Cookie值不能为空")
            sys.exit(1)

    return args


def main():
    """主程序流程"""
    # 设置目录结构
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # 获取Cookie
    args = get_args()

    parsed_file = data_dir / f"{args.start}_{args.end}.csv"
    if parsed_file.exists():
        print(f"已存在解析后的数据: {parsed_file}")
    else:
        print("正在获取数据...")
        fetcher = Fetcher(args.cookie)
        user_info = fetcher.get_user_info()
        print(user_info)
        records = fetcher.get_records(start=args.start, end=args.end)
        df = pd.DataFrame(records)
        df.to_csv(parsed_file, index=False, encoding='utf-8')
        print(f"解析后的数据已保存至: {parsed_file}")

    analyze(parsed_file)


if __name__ == "__main__":
    main()
