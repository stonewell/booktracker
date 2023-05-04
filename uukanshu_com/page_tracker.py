from .page_parser import PageParser
from page_tracker_base import PageTrackerBase


class PageTracker(PageTrackerBase):

  def __init__(self, url, _dir, timeout):
    super().__init__(url, _dir, timeout)

  def _get_page_parser(self):
    return PageParser()

  def _norm_content(self, content):
    return content.replace('UU看书', '').replace('www.uukanshu.com', '')
