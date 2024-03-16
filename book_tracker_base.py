import sys
import logging
import json
import time
import random

from urllib.error import URLError
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
        self.headers_ = []

        self._do_init()

    def __get_url(self):
        return self.url_

    def __set_url(self, url):
        self.url_ = url

    url = property(__get_url, __set_url)

    def __get_author(self):
        return self.author_

    def __set_author(self, author):
        self.author_ = author

    author = property(__get_author, __set_author)

    def __get_title(self):
        return self.title_

    def __set_title(self, title):
        self.title_ = title

    title = property(__get_title, __set_title)

    def __get_headers(self):
        return self.headers_

    def __set_headers(self, headers):
        self.headers_ = headers

    headers = property(__get_headers, __set_headers)

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

    def _get_page_tracker(self, page_key, page_url, content_dir, timeout):
        raise ValueError('no impl')

    def _need_read_page_content(self, response):
        return True

    def _get_page_url(self, page_file):
        return self.url_.replace('index.html', page_file)

    def _get_chapter_local_file(self, chapter_url):
        return chapter_url

    def refresh(self):
        with open_url(self.url_, self.timeout_) as response:

            if not self._need_read_page_content(response):
                return 0

            parser = self._get_index_parser()
            r_data = response.read()

            if not isinstance(r_data, str):
              try:
                r_data = r_data.decode(response
                                            .headers.get_content_charset() or 'gb18030')
              except:
                try:
                  r_data = r_data.decode('gb18030')
                except:
                  r_data = r_data.decode('utf-8')

            parser.feed(r_data)

            self.title = self.idx_['title'] = self.title_ if len(self.title_) > 0 else self._get_title(parser.title_)
            self.author = self.idx_['author'] = self.author_ if len(self.author_) > 0 else parser.author_

            chapters = parser.get_chapters()

            update_count = 0

            content_dir = self.book_dir_ / 'content/'

            content_dir.mkdir(parents=True, exist_ok=True)

            try:
                retry_count = 0
                for i in range(len(self.idx_['chapters'])):
                    page_key, page_file = self.idx_['chapters'][i]
                    page_url = self._get_page_url(page_file)

                    page = self._get_page_tracker(page_key, page_url, content_dir,
                                              self.timeout_)
                    page.extra_headers = self._get_extra_headers()

                    logging.debug("update existing page:%s", page_url)
                    try:
                        update_count += page.refresh()
                    except (NeedLoginError, NotFreeError) as err:
                        raise err
                    except URLError:
                        logging.exception("Failed update page:%s", page_url)
                        time.sleep(random.randrange(2, 8))
                        retry_count += 1
                        if retry_count > 10:
                          break
                    except:
                        logging.exception("Failed update page:%s", page_url)

                for i in range(len(self.idx_['chapters']), len(chapters)):
                    page_key, page_file = chapters[i]
                    page_url = self._get_page_url(page_file)

                    page = self._get_page_tracker(page_key, page_url, content_dir,
                                                  self.timeout_)
                    page.extra_headers = self._get_extra_headers()

                    logging.debug("update new page:%s", page_url)
                    try:
                        update_count += page.refresh()
                    except (NeedLoginError, NotFreeError) as err:
                        raise err
                    except URLError:
                        logging.exception("Failed update page:%s", page_url)
                        time.sleep(random.randrange(2, 8))
                        retry_count += 1
                        if retry_count > 10:
                          break
                    except:
                        logging.exception("Failed update page:%s", page_url)
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
                         self.idx_['chapters'],
                         self._get_chapter_local_file)
        eb.build()

    def _get_extra_headers(self):
        if not self.headers_ or len(self.headers_) == 0:
            return {}

        extra_headers = {}

        for header in self.headers_:
            parts = header.split('=')

            extra_headers[parts[0]] = '='.join(parts[1:])

        return extra_headers
