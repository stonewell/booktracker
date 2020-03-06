import logging
import json

from exceptions import NeedLoginError, NotFreeError
from pathlib import Path
from utils.epub_builder import EPubBuilder
from utils.url_helper import open_url


class TrackerBase(object):
    def __init__(self, url, author, title, data_dir, timeout):
        super().__init__()

        self.url_ = url
        self.data_dir_ = data_dir
        self.timeout_ = timeout
        self.author_ = author
        self.title_ = title

        self._do_init()

    def _parse_url(self):
        self.prefix_ = Path(self.url_).parts[-2]

    def _do_init(self):
        self._parse_url()
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

    def _get_title(self, title):
        raise ValueError('no title impl')

    def _get_index_parser(self):
        raise ValueError('no impl')

    def _get_page_tracker(self, page_url, content_dir, timeout):
        raise ValueError('no impl')

    def _need_read_page_content(self, response):
        return True

    def _get_page_url(self, page_file):
        return self.url_.replace('index.html', page_file)

    def refresh(self):
        with open_url(self.url_, self.timeout_) as response:

            if not self._need_read_page_content(response):
                return 0

            parser = self._get_index_parser()
            r_data = response.read().decode(response
                                            .headers.get_content_charset() or 'gb18030')
            parser.feed(r_data)

            self.title = self.idx_['title'] = self.title_ if len(self.title_) > 0 else self._get_title(parser.title_)
            self.author = self.idx_['author'] = self.author_ if len(self.author_) > 0 else parser.author_

            chapters = parser.get_chapters()

            update_count = 0

            content_dir = self.book_dir_ / 'content/'

            content_dir.mkdir(parents=True, exist_ok=True)

            try:
                for i in range(len(self.idx_['chapters'])):
                    page_key, page_file = self.idx_['chapters'][i]
                    page_url = self._get_page_url(page_file)

                    page = self._get_page_tracker(page_url, content_dir,
                                              self.timeout_)
                    update_count += page.refresh()

                for i in range(len(self.idx_['chapters']), len(chapters)):
                    page_key, page_file = chapters[i]
                    page_url = self._get_page_url(page_file)

                    page = self._get_page_tracker(page_url, content_dir,
                                              self.timeout_)
                    update_count += page.refresh()
            except NeedLoginError:
                logging.error('{} need to relogin from browser'.format(self.url_))
            except NotFreeError:
                logging.error('{} need to purchase first, not free book'.format(self.url_))

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
