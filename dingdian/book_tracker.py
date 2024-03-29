from .index_parser import IndexParser
from .page_tracker import PageTracker
from book_tracker_base import TrackerBase


class Tracker(TrackerBase):
    def __init__(self, url, author, title, data_dir, timeout):
        super().__init__(url, author, title, data_dir, timeout)

    def _get_title(self, title):
        return title

    def _get_index_parser(self):
        return IndexParser()

    def _get_page_tracker(self, page_key, page_url, content_dir, timeout):
        return PageTracker(page_url, content_dir, timeout)
