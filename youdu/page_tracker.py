from youdu.page_parser import PageParser, NeedLoginError
from page_tracker_base import PageTrackerBase
from pathlib import Path


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
