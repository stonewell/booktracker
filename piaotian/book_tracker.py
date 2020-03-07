import datetime

from piaotian.index_parser import IndexParser
from piaotian.page_tracker import PageTracker
from book_tracker_base import TrackerBase

class Tracker(TrackerBase):
    def __init__(self, url, author, title, data_dir, timeout):
        super().__init__(url, author, title, data_dir, timeout)

    def _get_title(self, title):
        idx = title.find('最新章节')

        return title[:idx]

    def _get_index_parser(self):
        return IndexParser()

    def _get_page_tracker(self, page_key, page_url, content_dir, timeout):
        return PageTracker(page_url, content_dir, timeout)

    def _need_read_page_content(self, response):
        m_time = datetime.datetime.strptime(response
                                            .info()['Last-Modified'],
                                            '%a, %d %b %Y %H:%M:%S %Z').timestamp()

        if 'title' in self.idx_ and m_time <= self.idx_['m_time'] and 'author' in self.idx_:
            self.title = self.__get_title(self.idx_['title'])
            self.author = self.idx_['author']
            return False

        return True
