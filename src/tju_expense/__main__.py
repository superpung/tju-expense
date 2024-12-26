#
# Created on Sun Dec 22 2024
#
# Copyright (c) 2024 Super Lee
#

import os
import sys
import argparse
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from matplotlib import font_manager
from rich.console import Console
from rich.prompt import Prompt
from tju_expense.analyze import analyze, print_statistics
from tju_expense.fetch import URLS, Fetcher
from importlib.metadata import version

console = Console()
error_console = Console(stderr=True)

def get_args():
    """Get command line arguments, including Cookie value and date range"""
    parser = argparse.ArgumentParser(description='Fetch and analyze transaction data')
    parser.add_argument('--cookie', help='Login Cookie')
    parser.add_argument('--year', help='Year')
    args = parser.parse_args()

    if not args.cookie:
        load_dotenv()
        args.cookie = os.getenv('COOKIE')

    if not args.cookie:
        console.log(f"未定义 Cookie, 请根据以下步骤获取 Cookie:")
        console.print(f"1. 使用浏览器访问天津大学财务处官网 {URLS['finance']} , 点击\"一卡通服务平台\" (或直接访问校园卡网站 {URLS['login']} ) 并登录")
        console.print(f"2. F12 打开 开发者工具 - Application - Storage - Cookies, 拷贝其中 JSESSIONID 的 Value")
        args.cookie = Prompt.ask("3. 粘贴 Cookie 至此处")
        if not args.cookie:
            error_console.log("[red]Cookie 不能为空")
            sys.exit(1)

    return args

def get_font_path():
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        base_path = Path(sys._MEIPASS) / "tju_expense"
    else:
        # 如果是开发环境
        base_path = Path(__file__).parent

    return base_path / "LXGWWenKaiLite-Regular.ttf"

def main():
    """Main program flow"""
    console.rule(f"[bold]TJU Expense[/bold] [dim]v{version('tju-expense')}[/dim]")
    console.rule(f"[italic]https://github.com/superpung/tju-expense")

    # 设置字体
    font_path = get_font_path()
    font_manager.fontManager.addfont(str(font_path))

    # Set up directory structure
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Get Cookie
    args = get_args()

    try:
        fetcher = Fetcher(args.cookie)
    except ConnectionError as e:
        error_console.log(f"[red]{e}")
        sys.exit(1)

    user_info = fetcher.get_user_info()
    console.print(f"你好, [bold]{user_info['name']}[/bold]!")

    user_dir = data_dir / user_info['stuid']
    user_dir.mkdir(exist_ok=True)

    if args.year and args.year.isdigit() and 2000 <= int(args.year) <= datetime.now().year:
        year = args.year
    else:
        year = datetime.now().year

    start, end = f"{year}-01-01", f"{year}-12-31"
    console.rule(f"[bold]{year} 年")
    console.log(f"正在获取 {year} 年的数据...")

    filename = f"{year}"
    parsed_file = user_dir / f"{filename}.csv"
    if parsed_file.exists():
        console.log(f"数据已经存在: {parsed_file}\n")
    else:
        records = fetcher.get_records(start=start, end=end)
        df = pd.DataFrame(records)
        df.to_csv(parsed_file, index=False, encoding='utf-8')
        console.log(f"数据已保存到 {parsed_file}")

    print_statistics(parsed_file)

    with console.status("[bold green]正在绘制年度总结图表...") as status:
        fig_file = user_dir / f"{filename}.png"
        analyze_result = analyze(parsed_file, title=f"在天大的{year}", save_to=fig_file)
        if analyze_result:
            console.log(f"年度总结图表绘制完成! 已保存到 {fig_file}")

    console.rule()
    console.input(f"[green]以上是你的 {year} 年度消费报告, 请查收![/green] [dim]按 Enter 退出...[/dim]")


if __name__ == "__main__":
    main()
