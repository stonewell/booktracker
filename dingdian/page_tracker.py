import urllib.request

from pathlib import Path
from dingdian.page_parser import PageParser


class PageTracker(object):
    def __init__(self, url, dir, timeout):
        super().__init__()

        self.url_ = url
        self.dir_ = dir
        self.timeout_ = timeout

        self.__do_init()

    def __parse_url(self):
        self.file_name_ = Path(self.url_).parts[-1]
        self.local_file_path_ = Path(self.dir_) / self.file_name_

    def __do_init(self):
        self.__parse_url()

    def refresh(self):
        if self.local_file_path_.exists():
            return 0

        with urllib.request.urlopen(self.url_, timeout=self.timeout_) as response:
            parser = PageParser()
            raw_data = response.read()
            r_data = raw_data.decode(response
                                     .headers.get_content_charset(),
                                     'ignore')

            parser.feed(r_data)

            with self.local_file_path_.open('wb') as f:
                f.write(parser.content.encode('utf8'))

        return 1
