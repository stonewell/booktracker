from .page_parser import PageParser
from page_tracker_base import PageTrackerBase


class PageTracker(PageTrackerBase):
    def __init__(self, url, dir, timeout):
        super().__init__(url, dir, timeout)

    def _get_page_parser(self):
        return PageParser()

    def _should_write_content(self, parser):
        if parser.content.find('正在手打中，请稍等片刻') >= 0:
            return False
        return True
