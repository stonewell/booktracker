from html.parser import HTMLParser


class IndexParser(HTMLParser):
    def __init__(self):
        super().__init__()

        self.in_a_ = False
        self.a_data_ = None
        self.a_href_ = None

        self.in_dd_ = False

        self.chapters_ = []

        self.title_ = ''
        self.author_ = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'dd':
            self.in_dd_ = True
        elif tag == 'a' and self.in_dd_:
            self.in_a_ = True
            for key, value in attrs:
                if key == 'href':
                    self.a_href_ = value
        elif tag == 'meta':
            author = ''
            found_author = False
            title = ''
            found_title = False
            for key, value in attrs:
                if key == 'property' and value == 'og:novel:author':
                    found_author = True
                elif found_author and key == 'content':
                    author = value
                elif key == 'property' and value == 'og:title':
                    found_title = True
                elif found_title and key == 'content':
                    title = value

            if found_author:
                self.author_ = author

            if found_title:
                self.title_ = title

    def is_chapter(self):
        return not (self.a_href_.startswith('javascript:')
                    or self.a_href_.startswith('#'))

    def handle_endtag(self, tag):
        if tag == 'dd':
            self.in_dd_ = False

        if tag == 'a':
            if self.in_a_:
                if self.is_chapter():
                    self.chapters_.append((self.a_data_, self.a_href_))
            self.in_a_ = False

    def data_to_bytes(self, data):
        x = 0
        buf = []

        while x < len(data):
            if x < len(data) - 3:
                if data[x] == '\\' and data[x+1] == 'x':
                    buf.append(int(data[x + 2: x + 4], 16))
                    x += 4
                    continue

            buf.append(ord(data[x]))
            x += 1

        return bytes(buf)

    def handle_data(self, data):
        if self.in_a_:
            self.a_data_ = data

    def get_chapters(self):
        c = {}
        for data, href in self.chapters_:
            c[href] = (data, href)

        def get_key(item):
            return int(item[1].replace('.html', ''))

        return sorted([c[key] for key in c], key=get_key)
