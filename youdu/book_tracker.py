from youdu.index_parser import IndexParser
from youdu.page_tracker import PageTracker
from book_tracker_base import TrackerBase
from pathlib import Path


class Tracker(TrackerBase):
    def __init__(self, url, author, title, data_dir, timeout):
        super().__init__(url, author, title, data_dir, timeout)

    def _get_title(self, title):
        return title

    def _get_index_parser(self):
        return IndexParser()

    def _get_page_tracker(self, page_key, page_url, content_dir, timeout):
        return PageTracker(page_key, page_url, content_dir, timeout)

    def _get_page_url(self, page_file):
        return page_file

    def _parse_url(self):
        self.prefix_ = 'youdu_' + Path(self.url_).parts[-1]

    def _get_chapter_local_file(self, chapter_url):
        return Path(chapter_url).parts[-1] + '.html'
