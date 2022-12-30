import random
import re
import socket
from http.client import HTTPSConnection, HTTPConnection, HTTPResponse
from urllib.parse import urlparse, ParseResult

REQUEST_USER_AGENTS = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 7.1.1; Moto G (5S) Build/NPPS26.102-49-11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.91 Mobile Safari/537.36',
    'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15',
    'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18',
    'SpecialAgent/13.0 (NSA 66.6 Linux) Magickal/3.14 (KHTML, like Gecko) Version/13.0.0'
]

class HttpRequest:
    def __init__(self, url: str, time_out: int = 10):
        self.url: ParseResult = None
        self.timeout: int = time_out
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
        host_name = socket.gethostbyname(socket.gethostname())

        if self.port == 443:
            self.connection = HTTPSConnection(self.url.netloc, timeout=self.timeout)
        else:
            self.connection = HTTPConnection(self.url.netloc, timeout=self.timeout)

    def add_header(self, n: str, v: str) -> None:
        self.headers[n] = v

    def get(self) -> HTTPResponse:
        random_ua: str = random.choice(REQUEST_USER_AGENTS)

        # randomize the User-Agent name
        # rand_hash = hex(crc32(datetime.now().isoformat().encode('utf8')))[2:]
        # self.add_header('User-Agent',f"special-agent-{rand_hash}-browser/2.0")

        # self.add_header('Host', random_host)
        self.add_header('User-Agent', random_ua)
        self.add_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.add_header('Pragma', 'no-cache')
        self.add_header('Expires', '0')
        self.add_header('Accept', '*/*')
        self.add_header('Accept-Language', '*/*')
        self.add_header('Accept-Encoding', '*/*')
        self.add_header('Connection', 'keep-alive')

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
