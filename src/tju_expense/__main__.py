import os
import sys
import argparse
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

from .analyze import analyze
from .fetch import Fetcher


def get_args():
    """Get command line arguments, including Cookie value and date range"""
    parser = argparse.ArgumentParser(description='Fetch and analyze transaction data')
    parser.add_argument('--cookie', help='Login Cookie')
    parser.add_argument('--start', help='Start date', default='2022-12-01')
    parser.add_argument('--end', help='End date', default='2022-12-31')
    args = parser.parse_args()

    if not args.cookie:
        load_dotenv()
        args.cookie = os.getenv('COOKIE')

    if not args.cookie:
        print("Please enter the login Cookie value:")
        args.cookie = input().strip()
        if not args.cookie:
            print("Error: Cookie value cannot be empty")
            sys.exit(1)

    return args


def main():
    """Main program flow"""
    # Set up directory structure
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Get Cookie
    args = get_args()

    fetcher = Fetcher(args.cookie)
    user_info = fetcher.get_user_info()
    print(user_info)

    user_dir = data_dir / user_info['stuid']
    user_dir.mkdir(exist_ok=True)
    filename = f"{args.start}_{args.end}"

    parsed_file = user_dir / f"{filename}.csv"
    if parsed_file.exists():
        print(f"Data already exists: {parsed_file}")
    else:
        records = fetcher.get_records(start=args.start, end=args.end)
        df = pd.DataFrame(records)
        df.to_csv(parsed_file, index=False, encoding='utf-8')
        print(f"Data saved to {parsed_file}")

    analyze(parsed_file, save_to=user_dir / f"{filename}.png")


if __name__ == "__main__":
    main()
