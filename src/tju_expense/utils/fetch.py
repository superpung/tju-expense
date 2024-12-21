import requests
import re

def fetch(cookie, raw_file):
    if cookie is None:
        raise ValueError("cookie is None")
    index_url = "http://59.67.37.10:8180/epay/myepay/index"
    index_response = requests.get(index_url, headers={"Cookie": cookie}).text
    meta_match = re.search(r'<meta name="_csrf" content="([^"]+)"', index_response)
    if meta_match:
        csrf = meta_match.group(1)
    else:
        raise ValueError("无法获取CSRF token")
    url = "http://59.67.37.10:8180/epay/consume/query"
    data = {
        "pageNo": 1,
        "tabNo": 1,
        "pager.offset": 0,
        "tradename": "",
        "starttime": "2023-01-01",
        "endtime": "2023-12-31",
        "timetype": 1,
        "_tradedirect": "on",
        "_csrf": csrf
    }

    headers = {
        "Cookie": cookie
    }

    response = requests.post(url, headers=headers, data=data)

    with open(raw_file, "w", encoding="utf-8") as f:
        f.write(response.text)
