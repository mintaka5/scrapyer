import os.path
from pathlib import Path

from bs4 import BeautifulSoup

from scrapyer.httprequest import HttpRequest


class DocumentProcessor:
    def __init__(self, req: HttpRequest, p: Path):
        self.sources: list = []
        self.save_path: Path = p
        self.request: HttpRequest = req
        response = self.request.get()
        self.dom: BeautifulSoup = BeautifulSoup(response.read(), 'html.parser')
        self.pop_sources()
        self.store_sources()
        self.js_path: Path = self.save_path.joinpath("js")
        self.css_path: Path = self.save_path.joinpath("css")
        self.create_paths()

    def create_paths(self) -> None:
        if not self.save_path.exists():
            self.save_path.mkdir(exist_ok=True, parents=True)

        if not self.js_path.exists():
            self.js_path.mkdir(exist_ok=True)

        if not self.css_path.exists():
            self.css_path.mkdir(exist_ok=True)

    def store_sources(self) -> None:
        if len(self.sources) > 0:
            for s in self.sources:
                self.store_url(s)

    def store_url(self, s: str) -> None:
        req = HttpRequest(s)
        res = req.get()
        # content = res.read()
        # @todo figure out how to map script file to paths

    def pop_sources(self):
        script_tags = self.dom.find_all('script')
        link_tags = self.dom.find_all('link')

        for st in script_tags:
            try:
                js = self.request.absolute_source(st['src'])
                self.sources.append(js)
            except KeyError as e:
                # src attribute was never found in script tags
                pass

        for lt in link_tags:
            try:
                ss_index = lt['rel'].index('stylesheet')
                lh = self.request.absolute_source(lt['href'])
                self.sources.append(lh)
            except ValueError as e:
                # stylesheet was never found in rel attribute list
                pass
