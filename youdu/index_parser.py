from html.parser import HTMLParser
from index_parser_base import IndexParserBase
from pathlib import Path


class IndexParser(HTMLParser, IndexParserBase):
    def __init__(self):
        super().__init__()

        self.in_a_ = False
        self.a_data_ = None
        self.a_href_ = None

        self.in_span_ = False
        self.cur_volume_ = ''

        self.in_chapter_list_ = False
        self.in_volume_name_ = False

        self.chapters_ = []

        self.title_ = ''
        self.author_ = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for key, value in attrs:
                if key == 'class' and value == 'chapter_list':
                    self.in_chapter_list_ = True
                if key == 'class' and value == 'volume_name':
                    self.in_volume_name_ = True
        elif tag == 'a' and self.in_chapter_list_:
            self.in_a_ = True
            for key, value in attrs:
                if key == 'onclick':
                    self.a_href_ = value.replace("ChapterGotoUrl('", "").replace("');", "")
        elif tag == 'span' and self.in_volume_name_:
            self.in_span_ = True

    def is_chapter(self):
        return not (self.a_href_.startswith('javascript:')
                    or self.a_href_.startswith('#'))

    def handle_endtag(self, tag):
        if tag == 'div':
            self.in_chapter_list_ = False
            self.in_volume_name_ = False

        if tag == 'span':
            self.in_span_ = False

        if tag == 'a':
            if self.in_a_:
                if self.is_chapter():
                    href = self.a_href_.replace('https://www.youdubook.com/readchapter/',
                                               'https://www.youdubook.com/booklibrary/membersinglechapter/chapter_id/')
                    self.chapters_.append((self.a_data_, href))
            self.in_a_ = False

    def handle_data(self, data):
        if self.in_a_:
            self.a_data_ = data
        if self.in_span_:
            self.cur_volume_ = data

    def _get_key(self, item):
        return int(Path(item[1]).parts[-1])
