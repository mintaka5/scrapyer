import sys
from binascii import crc32
from datetime import datetime
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
        rand_hash = hex(crc32(datetime.now().isoformat().encode('utf8')))[2:]
        request.add_header("User-Agent", f"special-agent-{rand_hash}-browser/1.0")

        '''
        process content
        '''
        doc = DocumentProcessor(request, save_path)
    except IndexError as e:
        print("1st and 2nd arguments required (e.g. scrapyer <url> <save path>)")
