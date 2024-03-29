from page_tracker_base import PageTrackerBase
from .page_parser import PageParser


class PageTracker(PageTrackerBase):
    def __init__(self, url, dir, timeout):
        super().__init__(url, dir, timeout)

    def _get_page_parser(self):
        return PageParser()

    def _norm_content(self, content):
      idx = content.find('重要声明：小说“')

      if idx >= 0:
        return content[:idx] + '</body></html>'
      return content
