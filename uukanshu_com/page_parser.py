from html.parser import HTMLParser


class PageParser(HTMLParser):

  def __init__(self):
    super().__init__()

    self.div_stack_ = 0
    self.in_content_ = False
    self.in_a_ = False
    self.in_h1_ = False
    self.in_ad_ = False

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
    elif tag == 'a':
      self.in_a_ = True
    elif tag == 'div':
      for key, value in attrs:
        if key == 'id' and value == 'contentbox':
          self.in_content_ = True
        elif key == 'class' and value == 'ad_content':
          self.in_ad_ = self.in_content_

  def handle_endtag(self, tag):
    if tag == 'h1' and self.in_h1_:
      self.content += '</h1>'
      self.in_h1_ = False
    elif tag == 'html':
      self.content += '</body></html>'
    elif tag == 'a':
      self.in_a_ = False
    elif tag == 'div' and self.in_content_:
      if self.in_ad_:
        self.in_ad_ = False
      else:
        self.in_content_ = False

  def handle_entityref(self, name):
    if self.in_content_ and not self.in_a_ and not self.in_ad_:
      self.content += ''.join(['&', name, ';'])

  def handle_charref(self, name):
    if self.in_content_ and not self.in_a_ and not self.in_ad_:
      self.content += ''.join(['&#', name, ';'])

  def handle_data(self, data):
    if (self.in_content_
        or self.in_h1_) and not self.in_a_ and not self.in_ad_:
      self.content += data
