from html.parser import HTMLParser
from index_parser_base import IndexParserBase


class IndexParser(HTMLParser, IndexParserBase):
    def __init__(self):
        super().__init__()

        self.in_content_ = False

        self.in_a_ = False
        self.a_data_ = None
        self.a_href_ = None

        self.in_td_ = False

        self.chapters_ = []

        self.in_title_ = False
        self.title_ = ''
        self.author_ = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.in_content_ = True
        elif tag == 'td' and self.in_content_:
            self.in_td_ = True
        elif tag == 'a' and self.in_td_:
            self.in_a_ = True
            for key, value in attrs:
                if key == 'href':
                    self.a_href_ = value
        elif tag == 'title':
            self.in_title_ = True

    def is_chapter(self):
        return len(self.a_href_) > 0 and not (self.a_href_.startswith('javascript:')
                    or self.a_href_.startswith('#'))

    def handle_endtag(self, tag):
        if tag == 'table' and self.in_content_:
            self.in_content_ = False

        if tag == 'td':
            self.in_td_ = False

        if tag == 'a':
            if self.in_a_:
                if self.is_chapter():
                    self.chapters_.append((self.a_data_, self.a_href_))
            self.in_a_ = False

        if tag == 'title':
            self.in_title_ = False

    def handle_data(self, data):
        if self.in_a_:
            self.a_data_ = data

        if self.in_title_:
            self.title_ = data

    def _get_key(self, item):
        return item[1].replace('.html', '')