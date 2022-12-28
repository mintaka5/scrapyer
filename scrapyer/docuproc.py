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

        self.create_paths()

    def create_paths(self) -> None:
        if not self.save_path.exists():
            self.save_path.mkdir(exist_ok=True, parents=True)

    def store_url(self, s: str) -> None:
        req = HttpRequest(s)
        res = req.get()

        if res.status != 404:
            content = res.read()

            local_path = Path(req.url.path[1:])
            if local_path.suffix != "":
                local_path = self.save_path.joinpath(Path(req.url.path[1:]))
                if not local_path.exists():
                    try:
                        local_path.parent.mkdir(parents=True)
                        print(f"writing: {local_path}")
                        local_path.write_bytes(content)
                    except FileExistsError as e:
                        pass


    def pop_sources(self):
        script_tags = self.dom.find_all('script')
        link_tags = self.dom.find_all('link')

        for st in script_tags:
            try:
                js = self.request.absolute_source(st['src'])
                self.store_url(js)
            except KeyError as e:
                # src attribute was never found in script tags
                pass

        for lt in link_tags:
            try:
                ss_index = lt['rel'].index('stylesheet')
                lh = self.request.absolute_source(lt['href'])
                self.store_url(lh)
            except ValueError as e:
                # stylesheet was never found in rel attribute list
                pass
