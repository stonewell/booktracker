import json
import base64

class NeedLoginError(Exception):
    pass

class PageParser(object):
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

    def feed(self, data):
        data = json.loads(data)

        if data['status'] == 3:
            raise NeedLoginError()

        show_content = data['data']['show_content']

        def sort_key(val):
            return val['paragraph_index']

        for content_data in sorted(show_content, key=sort_key):
            content = base64.b64decode(content_data['content'])
            self.content += content.decode('utf-8')
            self.content += '<br/>'

        self.content += '</body></html>'
