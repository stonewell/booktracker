from html.parser import HTMLParser
from index_parser_base import IndexParserBase
from pathlib import Path
import re


class IndexParser(HTMLParser, IndexParserBase):

  def __init__(self):
    super().__init__()

    self.in_a_ = False
    self.a_data_ = None
    self.a_href_ = None

    self.in_dd_ = False

    self.chapters_ = []

    self.title_ = ''
    self.author_ = ''

  def handle_starttag(self, tag, attrs):
    if tag == 'ul':
      for key, value in attrs:
        if key == 'id' and value == 'chapterList':
          self.in_dd_ = True
    elif tag == 'a' and self.in_dd_:
      self.in_a_ = True
      for key, value in attrs:
        if key == 'href':
          self.a_href_ = value
    elif tag == 'meta':
      author = ''
      found_author = False
      title = ''
      found_title = False

      for key, value in attrs:
        if key == 'property' and value == 'og:novel:author':
          found_author = True
        elif found_author and key == 'content':
          author = value
        elif key == 'property' and value == 'og:novel:book_name':
          found_title = True
        elif found_title and key == 'content':
          title = value

      if found_author:
        self.author_ = author

      if found_title:
        self.title_ = title

  def is_chapter(self):
    return len(self.a_href_) > 0 and not (
        self.a_href_.startswith('javascript:') or self.a_href_.startswith('#'))

  def handle_endtag(self, tag):
    if tag == 'ul':
      self.in_dd_ = False

    if tag == 'a':
      if self.in_a_:
        if self.is_chapter():
          self.chapters_.append(
              (self.norm_chapter(self.a_data_), self.a_href_))
      self.in_a_ = False

  def handle_data(self, data):
    if self.in_a_:
      self.a_data_ = data

  def norm_chapter(self, data):
    return re.sub('（.*[推荐票|月票].*）', '', data)

  def _get_key(self, item):
    return int(Path(item[1]).parts[-1].replace('.html', ''))
