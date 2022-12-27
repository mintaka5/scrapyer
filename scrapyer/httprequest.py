import re
from http.client import HTTPSConnection, HTTPConnection, HTTPResponse
from urllib.parse import urlparse, ParseResult


class HttpRequest:
    def __init__(self, url: str):
        self.url: ParseResult = None
        self.timeout: int = 10
        self.connection: HTTPConnection | HTTPSConnection = None
        self.port: int = 80
        self.parse(url)
        self.body: str = None
        self.headers: dict = {}

    def parse(self, url: str) -> None:
        p = urlparse(url)
        self.url = p

        self.determine_port()
        self.set_connection()

    def determine_port(self) -> None:
        if self.url.scheme == 'https':
            self.port = 443
        else:
            self.port = 80

    def set_connection(self) -> None:
        if self.port == 443:
            self.connection = HTTPSConnection(self.url.netloc, timeout=self.timeout)
        else:
            self.connection = HTTPConnection(self.url.netloc, timeout=self.timeout)

    def add_header(self, n: str, v: str) -> None:
        self.headers[n] = v

    def get(self) -> HTTPResponse:
        self.connection.request("GET", self.url.path, body=self.body, headers=self.headers)

        return self.connection.getresponse()

    def build_url_path(self, path_only: bool = False) -> str:
        """
        rebuild only the path from the original full URL

        Returns:
            string including path, parameters, query, and fragments
        """

        p = ""

        p += self.url.path

        if path_only is False:
            if self.url.params != "":
                p += f":{self.url.params}"

            if self.url.query != "":
                p += f"?{self.url.query}"

            if self.url.fragment != "":
                p += f"#{self.url.fragment}"

        return p

    def absolute_source(self, p: str) -> str:
        r = ""

        if p.startswith("/"):
            # root path
            r = self.get_root_url() + p
        elif re.match('^https?\://', p):
            r = p
        else:
            # relative path
            r = self.get_relative_url() + p

        return r

    def get_relative_url(self):
        u = self.get_root_url() + self.build_url_path(path_only=True)

        return u

    def get_root_url(self) -> str:
        u = self.url.scheme + "://" + self.url.netloc

        return u
