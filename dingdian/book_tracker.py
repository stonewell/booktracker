from dingdian.index_parser import IndexParser
from dingdian.page_tracker import PageTracker
from book_tracker_base import TrackerBase


class Tracker(TrackerBase):
    def __init__(self, url, data_dir, timeout):
        super().__init__(url, data_dir, timeout)

    def _get_title(self, title):
        return title

    def _get_index_parser(self):
        return IndexParser()

    def _get_page_tracker(self, page_url, content_dir, timeout):
        return PageTracker(page_url, content_dir, timeout)
