import argparse
import sys


def args_parser():
    parser = argparse.ArgumentParser(prog='booktracker',
                                     description='book update tracker in python')
    parser.add_argument('-f', '--urls_file', type=argparse.FileType('r'), help='a file contains book urls', required=False)
    parser.add_argument('-l', '--url', type=str, help='a book url to track', required=False)
    parser.add_argument('-o', '--output', type=str, help='directory to store book content', required=True)
    parser.add_argument('--epub', action='store_true', help='generate epub of book', required=False)
    parser.add_argument('--timeout', type=int, help='network request timeout value, default=13s', required=False, default=13)
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
            urls.add(url)

    if parser.url:
        urls.add(parser.url)

    for url in sorted(urls):
        if url.find('piaotian') > 0:
            from piaotian.book_tracker import Tracker as PiaoTianTracker
            tracker = PiaoTianTracker(url, parser.output, parser.timeout)
        elif url.find('23us') > 0:
            from dingdian.book_tracker import Tracker as DingDianTracker
            tracker = DingDianTracker(url, parser.output, parser.timeout)
        update_count = tracker.refresh()
        print(tracker.title, 'update count:', update_count)
        if parser.epub:
            tracker.gen_epub()
