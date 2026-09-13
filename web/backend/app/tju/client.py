"""TJU campus-card web client: plaintext username/password login (Spring
Security form, no captcha), then reuse the proven scraping in the root
``tju_expense`` package.

The login mechanism mirrors the campus-card sites (``ecard.tju.edu.cn`` /
``59.67.37.10:8180``): the ``imageCodeName`` captcha on the page is not enforced
by ``j_spring_security_check``, so only ``j_username``, ``j_password`` and the
CSRF token are required.
"""
from __future__ import annotations

import re

import requests

from tju_expense.fetch import BASE_URL, REQUEST_TIMEOUT, URLS, Fetcher

LOGIN_PAGE = URLS["login"]
LOGIN_CHECK_URL = f"{BASE_URL}/epay/j_spring_security_check"

_CSRF_INPUT = re.compile(r'name="_csrf"\s+value="([^"]+)"')
_CSRF_META = re.compile(r'<meta name="_csrf" content="([^"]+)"')

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
_NETWORK_HINT = "[登录失败] 请确认正在使用校园网环境, 关闭终端代理, 或重启终端"


class LoginError(Exception):
    """Raised when a login attempt is rejected (bad credentials)."""


class TJUWebClient:
    """Logs a user into the campus-card system with username + password.

    After a successful login the authenticated ``JSESSIONID`` is handed to the
    existing :class:`tju_expense.fetch.Fetcher`, which already knows how to read
    user info and consumption records.
    """

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": _UA})
        self._fetcher: Fetcher | None = None

    def login(self, username: str, password: str) -> dict:
        """Submit the login form; return user info on success."""
        try:
            page = self.session.get(LOGIN_PAGE, timeout=REQUEST_TIMEOUT)
        except requests.exceptions.RequestException as exc:
            raise LoginError(_NETWORK_HINT) from exc

        match = _CSRF_INPUT.search(page.text) or _CSRF_META.search(page.text)
        if not match:
            raise LoginError(_NETWORK_HINT)
        csrf = match.group(1)

        try:
            resp = self.session.post(
                LOGIN_CHECK_URL,
                data={"j_username": username, "j_password": password, "_csrf": csrf},
                headers={"Referer": LOGIN_PAGE, "Origin": BASE_URL},
                timeout=REQUEST_TIMEOUT,
            )
        except requests.exceptions.RequestException as exc:
            raise LoginError(_NETWORK_HINT) from exc

        # The logged-in home page is a frameset; the login form is not.
        if "<frameset" not in resp.text:
            raise LoginError("用户名或密码错误，请重试。")

        cookie = self.jsessionid
        if not cookie:
            raise LoginError("登录失败：未能建立会话，请重试。")

        # Hand the authenticated cookie to the proven scraper.
        try:
            fetcher = Fetcher(cookie)
        except ConnectionError as exc:
            raise LoginError("用户名或密码错误，请重试。") from exc

        info = fetcher.get_user_info()
        if not info.get("name"):
            raise LoginError("用户名或密码错误，请重试。")

        self._fetcher = fetcher
        return info

    @property
    def jsessionid(self) -> str | None:
        return self.session.cookies.get("JSESSIONID")

    @property
    def fetcher(self) -> Fetcher:
        if self._fetcher is None:
            raise LoginError("尚未登录。")
        return self._fetcher

    def user_info(self) -> dict:
        return self.fetcher.get_user_info()

    def records(self, start: str, end: str) -> list[dict]:
        return self.fetcher.get_records(start=start, end=end)


__all__ = ["TJUWebClient", "LoginError"]
