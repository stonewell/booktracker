import datetime
from pathlib import Path

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

  def _need_read_page_content(self, response):
    last_modified = response.info()['Last-Modified']
    if not last_modified:
      return True

    m_time = datetime.datetime.strptime(
        last_modified, '%a, %d %b %Y %H:%M:%S %Z').timestamp()

    if 'title' in self.idx_ and m_time <= self.idx_[
        'm_time'] and 'author' in self.idx_:
      self.title = self._get_title(self.idx_['title'])
      self.author = self.idx_['author']
      return False

    return True

  def _get_page_url(self, page_file):
    return 'https://' + Path(self.url_).parts[1] + page_file

  def _get_chapter_local_file(self, chapter_url):
    f = Path(chapter_url).parts[-1].replace('#', '')

    if f.endswith('.html'):
      return f

    return f + ".html"

  def _parse_url(self):
    self.prefix_ = Path(self.url_).parts[-1]
