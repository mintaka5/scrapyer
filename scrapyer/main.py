import sys
from pathlib import Path, PurePath

from scrapyer.docuproc import DocumentProcessor
from scrapyer.httprequest import HttpRequest


def boot_up():
    try:
        url = sys.argv[1]
        print(f"URL: {url}")
        save_dir = sys.argv[2]
        save_path = Path(save_dir)
        print(f"Save path: {save_path}")

        request = HttpRequest(url)
        request.add_header("Accept", "*/*")
        request.add_header("User-Agent", "special-agent-browser/1.0")

        '''
        process content
        '''
        doc = DocumentProcessor(request, save_path)
    except IndexError as e:
        print("1st and 2nd arguments required (e.g. scrapyer <url> <save path>)")
