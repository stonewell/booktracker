from html.parser import HTMLParser


class PageParser(HTMLParser):

  def __init__(self):
    super().__init__()

    self.div_stack_ = 0
    self.in_content_ = False
    self.in_a_ = False
    self.in_h1_ = False
    self.content_div_count_ = 0

    self.content = '''
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
     <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
  </head>
  <body>
'''

  def handle_starttag(self, tag, attrs):
    if tag == 'h1':
      self.in_h1_ = True
      self.content += '<h1>'
    elif tag == 'br' and self.in_content_:
      self.content += '<br/>'
    elif tag == 'p' and self.in_content_:
      self.content += '<p>'
    elif tag == 'a':
      self.in_a_ = True
    elif tag == 'script':
      self.in_a_ = True
    elif tag == 'div':
      if self.in_content_:
        self.content_div_count_ += 1
      for key, value in attrs:
        if key == 'class' and value == 'content':
          self.in_content_ = True
          self.content_div_count_ = 1

  def handle_endtag(self, tag):
    if tag == 'h1' and self.in_h1_:
      self.content += '</h1>'
      self.in_h1_ = False
    elif tag == 'html':
      self.content += '</body></html>'
    elif tag in ('a', 'script'):
      self.in_a_ = False
    elif tag == 'div' and self.in_content_:
      self.content_div_count_ -= 1
      if self.content_div_count_ == 0:
        self.in_content_ = False
    elif tag == 'p' and self.in_content_:
      self.content += '</p>'

  def handle_entityref(self, name):
    if self.in_content_ and not self.in_a_:
      self.content += ''.join(['&', name, ';'])

  def handle_charref(self, name):
    if self.in_content_ and not self.in_a_:
      self.content += ''.join(['&#', name, ';'])

  def handle_data(self, data):
    if (self.in_content_ or self.in_h1_) and not self.in_a_:
      self.content += data
