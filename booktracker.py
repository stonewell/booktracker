import argparse
import sys

from piaotian.book_tracker import Tracker


def args_parser():
    parser = argparse.ArgumentParser(prog='booktracker',
                                     description='book update tracker in python')
    parser.add_argument('-f', '--urls_file', type=argparse.FileType('r'), help='a file contains book urls', required=False)
    parser.add_argument('-l', '--url', type=str, help='a book url to track', required=False)
    parser.add_argument('-o', '--output', type=str, help='directory to store book content', required=True)
    return parser

if __name__ == '__main__':
    parser = args_parser().parse_args()

    if parser.urls_file is None and parser.url is None:
        args_parser().print_usage()
        sys.exit()

    if parser.urls_file:
        for url in parser.urls_file:
            url = url.strip().replace('\n', '').replace('\r', '')
            tracker = Tracker(url.strip(), parser.output)
            update_count = tracker.refresh()
            print(tracker.title, 'update count:', update_count)

    if parser.url:
        tracker = Tracker(parser.url, parser.output)
        update_count = tracker.refresh()
        print(tracker.title, 'update count:', update_count)
