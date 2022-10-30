from pathlib import Path
from utils.url_helper import open_url


class PageTrackerBase(object):

  def __init__(self, url, dir, timeout):
    super().__init__()

    self.url_ = url
    self.dir_ = dir
    self.timeout_ = timeout
    self.extra_headers_ = {}

    self._do_init()

  def _parse_url(self):
    self.file_name_ = Path(self.url_).parts[-1]
    self.local_file_path_ = Path(self.dir_) / self.file_name_

  def _do_init(self):
    self._parse_url()

  def _get_page_parser(self):
    raise ValueError('no impl')

  def _should_write_content(self, parser):
    return True

  def _get_extra_headers(self):
    return self.extra_headers_

  def _set_extra_headers(self, extra_headers):
    self.extra_headers_ = extra_headers

  def _norm_content(self, content):
    return content

  extra_headers = property(_get_extra_headers, _set_extra_headers)

  def refresh(self):
    if self.local_file_path_.exists():
      return 0

    with open_url(self.url_, self.timeout_,
                  self._get_extra_headers()) as response:
      parser = self._get_page_parser()
      raw_data = response.read()
      r_data = raw_data.decode(
          response.headers.get_content_charset() or 'gb18030', 'ignore')

      parser.feed(r_data)

      if not self._should_write_content(parser):
        return 0

      with self.local_file_path_.open('wb') as f:
        f.write(self._norm_content(parser.content).encode('utf8'))

    return 1

  def login(self):
    pass
