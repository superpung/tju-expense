import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from .utils import fetch, parse, analyze

def setup_directories():
    """创建必要的目录结构"""
    data_dir = Path("data")
    raw_dir = data_dir / "raw"
    parsed_dir = data_dir / "parsed"
    
    for dir_path in [data_dir, raw_dir, parsed_dir]:
        dir_path.mkdir(exist_ok=True)
    
    return raw_dir, parsed_dir

def get_cookie():
    """获取Cookie值，优先从命令行参数获取，其次是环境变量，最后是用户输入"""
    parser = argparse.ArgumentParser(description='获取并分析交易数据')
    parser.add_argument('--cookie', help='登录Cookie')
    args = parser.parse_args()

    # 1. 检查命令行参数
    if args.cookie:
        return args.cookie

    # 2. 检查环境变量
    load_dotenv()  # 加载.env文件
    cookie = os.getenv('COOKIE')
    if cookie:
        return cookie

    # 3. 用户输入
    print("请输入登录Cookie值：")
    cookie = input().strip()
    if not cookie:
        print("错误：Cookie值不能为空")
        sys.exit(1)
    
    return cookie

def main():
    """主程序流程"""
    # 设置目录结构
    raw_dir, parsed_dir = setup_directories()
    
    # 获取Cookie
    cookie = get_cookie()
    
    # 生成时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # 1. 获取数据
        print("正在获取交易数据...")
        # raw_file = raw_dir / f"transactions_{timestamp}.html"
        raw_file = raw_dir / "data.html"
        fetch(cookie, raw_file)
        print(f"原始数据已保存至: {raw_file}")
        
        # 2. 解析数据
        print("\n正在解析数据...")
        parsed_file = parsed_dir / f"transactions_{timestamp}.csv"
        df = parse(raw_file)
        df.to_csv(parsed_file, index=False, encoding='utf-8')
        print(f"解析后的数据已保存至: {parsed_file}")
        
        # 3. 分析数据
        print("\n开始分析数据...")
        analyze(df)
        
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
