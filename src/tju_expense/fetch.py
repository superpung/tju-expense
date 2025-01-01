#
# Created on Sun Dec 22 2024
#
# Copyright (c) 2024 Super Lee
#

import re
import requests

from bs4 import BeautifulSoup
from rich.progress import track

BASE_URL = "http://59.67.37.10:8180"
URLS = {
    "repo": "https://github.com/superpung/tju-expense",
    "finance": "https://finance.tju.edu.cn/",
    "login": f"{BASE_URL}/epay/person/index",
    "user_info": f"{BASE_URL}/epay/personaccount/index",
    "records": f"{BASE_URL}/epay/consume/query",
}

class Fetcher:
    def __init__(self, cookie: str):
        if not cookie.startswith("JSESSIONID"):
            self.cookie = f"JSESSIONID={cookie}"
        else:
            self.cookie = cookie
        self.csrf = None
        self.user_info = self.fetch_user_info()

    def get_user_info(self):
        return self.user_info

    def fetch_user_info(self):
        url = URLS["user_info"]
        headers = {
            'Cookie': self.cookie
        }
        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.InvalidSchema as _:
            raise ConnectionError(f"[登录失败] 请确认正在使用校园网环境, 关闭终端代理, 或重启终端")
        soup = BeautifulSoup(response.text, 'html.parser')

        meta_match = re.search(r'<meta name="_csrf" content="([^"]+)"', response.text)
        if meta_match:
            self.csrf = meta_match.group(1)
        else:
            raise ConnectionError(f"[登录失败] 请访问 {URLS['login']} 重新获取 Cookie")

        res = {}

        for tr in soup.find_all('tr'):
            attr = []
            for td in tr.find_all('td'):
                text = ''.join(td.text.split())
                attr.append(text)

            if len(attr) != 2:
                continue
            if '学工号' in attr[0]:
                res['stuid'] = attr[1]
            elif '姓名' in attr[0]:
                res['name'] = attr[1]
            elif '现金资金' in attr[0]:
                res['balance'] = re.search('\\d+\\.\\d+', attr[1]).group()

        return res

    def get_records(self, start, end):
        """
        获取交易记录
        :param start: 开始日期，格式为2022-03-30
        :param end: 结束日期，格式为2022-03-30
        :return: 指定日期内的交易记录
        """
        records = []
        res1, cnt = self.get_record(start, end, 1)
        records.extend(res1)

        for i in track(range(2, cnt + 1)):
            res2, cnt = self.get_record(start, end, i)
            records.extend(res2)

        return records

    def get_record(self, start, end, page, include_top_up=False):
        url = URLS["records"]
        data = {
            "pageNo": page,
            "tabNo": "1",
            "pager.offset": (page - 1) * 10,
            "tradename": "",
            "starttime": start,
            "endtime": end,
            "timetype": "1",
            "_tradedirect": "on",
            "_csrf": self.csrf
        }
        if not include_top_up:
            data["tradedirect"] = "1"
        headers = {
            "Cookie": self.cookie
        }
        s = requests.session()
        response = s.post(url, data=data, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        res = []
        page_cnt = 1
        willend = False

        block_words = ['现金', '交易成功', '详情']

        for tr in soup.find_all('tr'):
            end = False
            record = {}

            for td in tr.find_all('td'):
                text = ''.join(td.text.split())

                if '当前' in text or (willend and '创建时间' in text):
                    end = True
                if '创建时间' in text:
                    willend = True
                    break
                if '当前' in text:
                    page_cnt = int(re.findall('\\d+', text)[1])
                    break

                if re.match('\\d+\\.\\d+\\.\\d+', text):
                    day = text.replace('.', '-')[0:10]
                    time = text[10:12] + ':' + text[12:14] + ':' + text[14:16]
                    record['time'] = day + ' ' + time
                elif re.match('.*交易号：\\d+', text):
                    record['id'] = re.search('20\\d+', text).group()
                    record['type'] = re.findall('.*交易号', text)[0].replace('交易号', '')
                elif re.match('\\d+\\.\\d+', text):
                    record['amount'] = text
                # -11.00为冲正类型，退款到卡内
                elif re.match('-\\d+\\.\\d+', text):
                    record['amount'] = text
                elif text not in block_words:
                    record['place'] = text

            if end:
                break

            if not record == {}:
                res.append(record)

        return res, page_cnt
