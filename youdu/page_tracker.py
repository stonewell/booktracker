from youdu.page_parser import PageParser
from page_tracker_base import PageTrackerBase
from pathlib import Path
from exceptions import NeedLoginError


class PageTracker(PageTrackerBase):
    def __init__(self, key, url, dir, timeout):
        super().__init__(url, dir, timeout)
        self.page_key_ = key

    def _get_page_parser(self):
        return PageParser(self.page_key_)

    def _should_write_content(self, parser):
        if parser.content.find('正在手打中，请稍等片刻') >= 0:
            return False
        return True

    def _parse_url(self):
        self.file_name_ = Path(self.url_).parts[-1] + ".html"
        self.local_file_path_ = Path(self.dir_) / self.file_name_

    def refresh(self):
        try:
            return super().refresh()
        except NeedLoginError:
            self.login()
            return super().refresh()

    def login(self):
        pass
