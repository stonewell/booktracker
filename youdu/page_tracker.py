from youdu.page_parser import PageParser
from page_tracker_base import PageTrackerBase
from pathlib import Path
from exceptions import NeedLoginError


class PageTracker(PageTrackerBase):
    def __init__(self, url, dir, timeout):
        super().__init__(url, dir, timeout)

    def _get_page_parser(self):
        return PageParser()

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

    def _get_extra_headers(self):
        return {'cookie': 'PHPSESSID=71g4k7048l6rn538jjk1ce6bse; saveMemberInfo=%7B%22username%22%3A%2213910399454%22%2C%22password%22%3A%22123456%22%7D'}
