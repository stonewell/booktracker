import argparse
import sys
import logging


def args_parser():
    parser = argparse.ArgumentParser(prog='booktracker',
                                     description='book update tracker in python')
    parser.add_argument('-f', '--urls_file', type=argparse.FileType('r'), help='a file contains book urls', required=False)
    parser.add_argument('-l', '--url', type=str, help='a book url to track', required=False)
    parser.add_argument('-o', '--output', type=str, help='directory to store book content', required=True)
    parser.add_argument('--epub', action='store_true', help='generate epub of book', required=False)
    parser.add_argument('--timeout', type=int, help='network request timeout value, default=13s', required=False, default=13)
    parser.add_argument('--author', type=str, help='author of the book', required=False, default='')
    parser.add_argument('--title', type=str, help='title of the book', required=False, default='')
    return parser

if __name__ == '__main__':
    parser = args_parser().parse_args()

    if parser.urls_file is None and parser.url is None:
        args_parser().print_usage()
        sys.exit()

    urls = set()

    if parser.urls_file:
        for url in parser.urls_file:
            url = url.strip().replace('\n', '').replace('\r', '')
            parts = url.split('|')
            urls.add((parts[0],
                      parts[1] if len(parts) > 1 else '',
                      parts[2] if len(parts) > 2 else '')
            )

    if parser.url:
        urls.add((parser.url, parser.author, parser.title))

    for url, author, title in sorted(urls):
        try:
            if url.find('piaotian') > 0:
                from piaotian.book_tracker import Tracker as PiaoTianTracker
                tracker = PiaoTianTracker(url, author, title, parser.output, parser.timeout)
            elif url.find('23us') > 0:
                from dingdian.book_tracker import Tracker as DingDianTracker
                tracker = DingDianTracker(url, author, title, parser.output, parser.timeout)
            elif url.find('youdubook') > 0:
                from youdu.book_tracker import Tracker as YouduTracker
                tracker = YouduTracker(url, author, title, parser.output, parser.timeout)

            update_count = tracker.refresh()
            print(tracker.title, 'update count:', update_count)
            if parser.epub:
                tracker.gen_epub()
        except:
            logging.exception("update failed")
            print('update failed:', url)
