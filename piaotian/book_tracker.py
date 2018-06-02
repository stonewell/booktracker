import json
import urllib.request
import datetime

from pathlib import Path
from piaotian.index_parser import IndexParser
from piaotian.page_tracker import PageTracker
from utils.epub_builder import EPubBuilder


class Tracker(object):
    def __init__(self, url, data_dir):
        super().__init__()

        self.url_ = url
        self.data_dir_ = data_dir

        self.__do_init()

    def __parse_url(self):
        self.prefix_ = Path(self.url_).parts[-2]

    def __do_init(self):
        self.__parse_url()
        self.book_dir_ = Path(self.data_dir_) / self.prefix_

        self.book_dir_.mkdir(parents=True, exist_ok=True)

        # load saved index
        self.idx_file_ = self.book_dir_ / (self.prefix_ + '_idex.json')

        if self.idx_file_.exists():
            self.idx_ = json.loads(self.idx_file_.read_text('utf8'))
        else:
            self.idx_ = {
                'url': self.url_,
                'm_time': 0,
                'chapters': [],
            }

    def __get_title(self, title):
        idx = title.find('最新章节')

        return title[:idx]

    def refresh(self):
        with urllib.request.urlopen(self.url_) as response:
            m_time = datetime.datetime.strptime(response
                                                .info()['Last-Modified'],
                                                '%a, %d %b %Y %H:%M:%S %Z').timestamp()

            if 'title' in self.idx_ and m_time <= self.idx_['m_time'] and 'author' in self.idx_:
                self.title = self.__get_title(self.idx_['title'])
                self.author = self.idx_['author']
                return 0

            parser = IndexParser()
            r_data = response.read().decode(response
                                            .headers.get_content_charset())
            parser.feed(r_data)

            self.title = self.idx_['title'] = self.__get_title(parser.title_)
            self.author = self.idx_['author'] = parser.author_

            chapters = parser.chapters_

            update_count = 0

            content_dir = self.book_dir_ / 'content/'

            content_dir.mkdir(parents=True, exist_ok=True)

            for i in range(len(self.idx_['chapters'])):
                page_key, page_file = self.idx_['chapters'][i]
                page_url = self.url_.replace('index.html', page_file)

                page = PageTracker(page_url, content_dir)
                update_count += page.refresh()

            for i in range(len(self.idx_['chapters']), len(chapters)):
                page_key, page_file = chapters[i]
                page_url = self.url_.replace('index.html', page_file)

                page = PageTracker(page_url, content_dir)
                update_count += page.refresh()

            if update_count == 0:
                return update_count

            self.idx_['chapters'] = chapters

            with self.idx_file_.open('wb') as f:
                i_data = json.dumps(self.idx_,
                                    ensure_ascii=False,
                                    indent=4)
                f.write(i_data.encode('utf8'))

            return update_count

    def gen_epub(self):
        content_dir = self.book_dir_ / 'content/'
        eb = EPubBuilder(self.title,
                         self.author,
                         str(self.book_dir_),
                         str(content_dir),
                         self.idx_['chapters'])
        eb.build()
