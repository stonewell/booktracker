import argparse
import sys
import logging
import json


def args_parser():
    parser = argparse.ArgumentParser(prog='booktracker',
                                     description='book update tracker in python')
    parser.add_argument('-f', '--urls_file', type=argparse.FileType('r'), help='a file contains book urls, could be a text file list urls or complex json file for url and attributes', required=False)
    parser.add_argument('-l', '--url', type=str, help='a book url to track', required=False)
    parser.add_argument('-o', '--output', type=str, help='directory to store book content', required=True)
    parser.add_argument('--epub', action='store_true', help='generate epub of book', required=False)
    parser.add_argument('--timeout', type=int, help='network request timeout value, default=13s', required=False, default=13)
    parser.add_argument('--author', type=str, help='author of the book', required=False, default='')
    parser.add_argument('--title', type=str, help='title of the book', required=False, default='')
    parser.add_argument('--header', type=str, action='append', help='http request header', required=False, dest='headers')
    parser.add_argument('-v', '--verbose', action='count', help='print debug information', required=False, default=0)
    return parser

def parse_urls_file_txt(urls_file):
    urls = set()

    for url in urls_file:
        url = url.strip().replace('\n', '').replace('\r', '')
        parts = url.split('|')

        headers = []

        if len(parts) > 3:
            headers = '|'.join(parts[3:]).split(',')

        urls.add(
            (parts[0],
             parts[1] if len(parts) > 1 else '',
             parts[2] if len(parts) > 2 else '',
             tuple(headers))
        )

    return urls

def parse_urls_file_json(urls_file):
    urls = set()

    books = json.load(urls_file)

    for book in books:
        url = book['url'].strip().replace('\n', '').replace('\r', '')
        author = book['author'].strip().replace('\n', '').replace('\r', '') if 'author' in book else ''
        title = book['title'].strip().replace('\n', '').replace('\r', '') if 'title' in book else ''
        headers = book['headers'] if 'headers' in book else []

        logging.debug('url:%s, author:%s, title:%s, headers:%s',
                          url, author, title, headers)
        urls.add((url, author, title, tuple(headers)))

    return urls


if __name__ == '__main__':
    parser = args_parser().parse_args()

    if parser.verbose >= 1:
        logging.getLogger('').setLevel(logging.DEBUG)

    if parser.urls_file is None and parser.url is None:
        args_parser().print_usage()
        sys.exit()

    urls = set()

    if parser.urls_file:
        try:
            urls = parse_urls_file_json(parser.urls_file)
        except:
            logging.exception('urls file:%s is not json try text file', parser.urls_file)
            parser.urls_file.seek(0)
            urls = parse_urls_file_txt(parser.urls_file)

    if parser.url:
        urls.add((parser.url,
                  parser.author,
                  parser.title,
                  tuple(parser.headers) if parser.headers else tuple([]))
        )

    for url, author, title, headers in sorted(urls):
        try:
            if url.find('piaotian') > 0 or url.find('ptwxz') > 0:
                from piaotian.book_tracker import Tracker as PiaoTianTracker
                tracker = PiaoTianTracker(url, author, title, parser.output, parser.timeout)
            elif url.find('23us') > 0:
                from dingdian.book_tracker import Tracker as DingDianTracker
                tracker = DingDianTracker(url, author, title, parser.output, parser.timeout)
            elif url.find('youdubook') > 0:
                from youdu.book_tracker import Tracker as YouduTracker
                tracker = YouduTracker(url, author, title, parser.output, parser.timeout)
            elif url.find('shuku') > 0:
                from shuku.book_tracker import Tracker as ShuKuTracker
                tracker = ShuKuTracker(url, author, title, parser.output, parser.timeout)
            elif url.find('uukanshu') > 0:
                from uukanshu.book_tracker import Tracker as UUKanShuTracker
                tracker = UUKanShuTracker(url, author, title, parser.output, parser.timeout)

            if not tracker:
                raise ValueError("tracker not found")
            tracker.headers = list(headers)

            update_count = tracker.refresh()
            print(tracker.title, 'update count:', update_count)
            if parser.epub:
                tracker.gen_epub()
        except:
            logging.exception("update failed:{}".format(url))
