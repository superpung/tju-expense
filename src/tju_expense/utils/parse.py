from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def parse(html_file):
    """解析交易记录HTML数据"""
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # 找到所有交易记录表格
    transactions = []

    # 查找所有交易行
    rows = soup.find_all('tr')

    for row in rows:
        # 跳过表头行
        if row.find('td', text='创建时间'):
            continue

        # 获取每行中的所有单元格
        cells = row.find_all('td')
        if len(cells) < 6:  # 确保行有足够的单元格
            continue

        try:
            # 解析时间
            time_div = cells[0].find('div')
            if not time_div:
                continue
            date_str = time_div.text.strip()
            time_code = cells[0].find('div', class_='span_2').text.strip()

            # 解析交易名称和编号
            trade_link = cells[1].find('a')
            if not trade_link:
                continue
            trade_name = trade_link.text.strip()
            trade_no = cells[1].find('div', class_='span_2').text.replace('交易号：', '').strip()

            # 解析其他信息
            counterparty = cells[2].text.strip()
            amount = cells[3].text.strip()
            payment_method = cells[4].text.strip()
            status = cells[5].find('span', class_='label').text.strip() if cells[5].find('span', class_='label') else ''

            transaction = {
                'time': date_str,
                'time_code': time_code,
                'trade_name': trade_name,
                'trade_no': trade_no,
                'counterparty': counterparty,
                'amount': amount,
                'payment_method': payment_method,
                'status': status
            }

            transactions.append(transaction)

        except Exception as e:
            print(f"解析行时出错: {e}")
            continue

    # 转换为DataFrame
    df = pd.DataFrame(transactions)

    # 清理数据
    df['amount'] = df['amount'].str.replace('&nbsp;', '').astype(float)
    df['payment_method'] = df['payment_method'].str.replace('&nbsp;', '').str.strip()

    return df
