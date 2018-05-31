from html.parser import HTMLParser


class IndexParser(HTMLParser):
    def __init__(self):
        super().__init__()

        self.div_stack_ = 0
        self.in_content_ = False

        self.in_a_ = False
        self.a_data_ = None
        self.a_href_ = None

        self.in_li_ = False

        self.chapters_ = []

        self.in_title_ = False
        self.title_ = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for key, value in attrs:
                if key == 'class' and value == 'centent':
                    # found the content div
                    self.in_content_ = True

            if self.in_content_:
                self.div_stack_ += 1
        elif tag == 'li' and self.in_content_:
            self.in_li_ = True
        elif tag == 'a' and self.in_li_:
            self.in_a_ = True
            for key, value in attrs:
                if key == 'href':
                    self.a_href_ = value
        elif tag == 'title':
            self.in_title_ = True

    def handle_endtag(self, tag):
        if tag == 'div' and self.in_content_:
            self.div_stack_ -= 1

        if tag == 'li':
            self.in_li_ = False

        if tag == 'a':
            if self.in_a_:
                self.chapters_.append((self.a_data_, self.a_href_))
            self.in_a_ = False

        if self.div_stack_ == 0:
            self.in_content_ = False

        if tag == 'title':
            self.in_title_ = False

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

        if self.in_title_:
            self.title_ = data
