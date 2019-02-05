from utils.url_helper import open_url
from pathlib import Path


class PageTrackerBase(object):
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

    def _get_page_parser(self):
        raise ValueError('no impl')

    def _should_write_content(self, parser):
        return True

    def refresh(self):
        if self.local_file_path_.exists():
            return 0

        with open_url(self.url_, self.timeout_) as response:
            parser = self._get_page_parser()
            raw_data = response.read()
            r_data = raw_data.decode(response
                                     .headers.get_content_charset() or 'gb18030',
                                     'ignore')

            parser.feed(r_data)

            if not self._should_write_content(parser):
                return 0

            with self.local_file_path_.open('wb') as f:
                f.write(parser.content.encode('utf8'))

        return 1
