import os
import sys
import argparse
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

from .analyze import analyze
from .fetch import Fetcher

def setup_directories():
    """创建必要的目录结构"""
    data_dir = Path("data")
    raw_dir = data_dir / "raw"
    parsed_dir = data_dir / "parsed"

    for dir_path in [data_dir, raw_dir, parsed_dir]:
        dir_path.mkdir(exist_ok=True)

    return raw_dir, parsed_dir

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
    raw_dir, parsed_dir = setup_directories()

    # 获取Cookie
    args = get_args()

    filename = f"{args.start}_{args.end}"
    parsed_file = parsed_dir / f"{filename}.csv"
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
