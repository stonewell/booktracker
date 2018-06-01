from html.parser import HTMLParser


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()

        self.div_stack_ = 0
        self.in_content_ = False
        self.in_a_ = False

        self.content = '''
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
     <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
  </head>
  <body>
'''

    def handle_starttag(self, tag, attrs):
        if tag == 'h1':
            self.in_content_ = True
            self.content += '<h1>'
        elif tag == 'br' and self.in_content_:
            self.content += '<br/>'
        elif tag == 'a':
            self.in_a_ = True

    def handle_endtag(self, tag):
        if tag == 'h1' and self.in_content_:
            self.content += '</h1>'
        elif tag == 'html':
            self.content += '</body></html>'
        elif tag == 'a':
            self.in_a_ = False

    def handle_entityref(self, name):
        if self.in_content_ and not self.in_a_:
            self.content += ''.join(['&', name, ';'])

    def handle_charref(self, name):
        if self.in_content_ and not self.in_a_:
            self.content += ''.join(['&#', name, ';'])

    def handle_comment(self, data):
        if data.strip() == '翻页上AD开始':
            self.in_content_ = False

    def handle_data(self, data):
        if self.in_content_ and not self.in_a_:
            self.content += data
