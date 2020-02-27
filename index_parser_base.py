class IndexParserBase(object):
    def _get_key(self, item):
        return int(item[1].replace('.html', ''))

    def get_chapters(self):
        c = {}
        for data, href in self.chapters_:
            c[href] = (data, href)

        return sorted([c[key] for key in c], key=self._get_key)

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
