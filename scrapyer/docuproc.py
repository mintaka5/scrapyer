from pathlib import Path
from time import sleep

from bs4 import BeautifulSoup

from scrapyer.docusource import DocumentSource, SourceType
from scrapyer.httprequest import HttpRequest


class DocumentProcessor:
    def __init__(self, req: HttpRequest, p: Path):
        self.dom: BeautifulSoup = None
        self.is_processing: bool = False
        self.save_path: Path = p

        self.sources: list[DocumentSource] = []
        
        self.request: HttpRequest = req

        # create storage path
        self.create_paths()

    def start(self):
        self.is_processing = True

        while self.is_processing is True:
            try:
                response = self.request.get()
                self.dom = BeautifulSoup(response.read(), 'html.parser')
                print(f"status: {response.status} {response.reason}")

                # save source files to storage directory
                self.pop_sources()
            except TimeoutError as e:
                sleep(self.request.timeout)
                continue

            self.save_html()

            self.is_processing = False

            [self.store_url(source) for source in self.sources]

    def save_html(self):
        # @todo store content in index.html file
        html_file = self.save_path.joinpath('index.html')
        if not html_file.exists():
            html_file.write_bytes(self.dom.prettify('utf8'))

        self.localize_html()

    def localize_html(self):
        html_file = self.save_path.joinpath('index.html')
        contents = html_file.read_bytes()
        html_text = contents.decode('utf8')
        # html_dom = BeautifulSoup(html_text, 'html.parser')
        for p in self.save_path.rglob('*.*'):
            if p.suffix != '.html':
                rel_path = p.relative_to(self.save_path)
                # result = html_text.find(str(rel_path).replace("\\", "/"))
                rel_urlized = rel_path.as_posix()
                # @todo: swap rel local path with html content's URL

    def create_paths(self) -> None:
        if not self.save_path.exists():
            self.save_path.mkdir(exist_ok=True, parents=True)

    def store_url(self, s: DocumentSource, parent_dirname = None) -> None:
        req = HttpRequest(s.url, time_out=self.request.timeout)
        res = req.get()

        # don't bother with 404s
        # print(f"status: {res.status} url: {s.url}")
        if res.status != 404:
            content = res.read()

            local_path = Path(req.url.path[1:])
            if parent_dirname is not None:
                local_path = Path(parent_dirname, req.url.path[1:])

            # has to have a file extension
            if local_path.suffix != "":
                local_path = self.save_path.joinpath(local_path)
                if not local_path.exists():
                    try:
                        local_path.parent.mkdir(parents=True)
                    except FileExistsError as e:
                        pass
                # store the files
                print(f"stored: {local_path}")
                local_path.write_bytes(content)


    def pop_sources(self):
        script_tags = self.dom.find_all('script')
        link_tags = self.dom.find_all('link')
        img_tags = self.dom.find_all('img')

        # @todo scan css for img URLs

        # @todo find inline style and script tags, save as files, and remove tags from body

        for it in img_tags:
            try:
                img = self.request.absolute_source(it['src'])
                self.sources.append(DocumentSource(SourceType.img, img))
                # self.store_url(img, parent_dirname='images')
            except KeyError as e:
                # no src attribute found
                pass

        for st in script_tags:
            try:
                # `src` attribute present so get javascript file content of URL
                js = self.request.absolute_source(st['src'])
                self.sources.append(DocumentSource(SourceType.js, js))
                # self.store_url(js, parent_dirname='js')
            except KeyError as e:
                # src attribute was never found in script tags
                pass

        for lt in link_tags:
            try:
                lt['rel'].index('stylesheet')
                lh = self.request.absolute_source(lt['href'])
                self.sources.append(DocumentSource(SourceType.css, lh))
                # self.store_url(lh, parent_dirname='css')
            except ValueError as e:
                pass