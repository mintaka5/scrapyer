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

    def store_sources(self):
        if len(self.sources) > 0:
            for s in self.sources:
                self.store_url(s)

    def store_url(self, s: str):
        req = HttpRequest(s)
        res = req.get()
        print(f"status: {res.status} >> {s}")

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
