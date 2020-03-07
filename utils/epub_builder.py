import logging
import os.path
import zipfile

from pathlib import Path

# We need an index file, that lists all other HTML files
# This index file itself is referenced in the META_INF/container.xml
# file
idx_data = '''<container version="1.0"
        xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
        <rootfiles>
        <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
        </rootfiles>
        </container>
'''

# The index file is another XML file, living per convention
# in OEBPS/Content.xml
index_tpl = '''<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="BookId">
  <metadata xmlns:calibre="http://calibre.kovidgoyal.net/2009/metadata" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:opf="http://www.idpf.org/2007/opf" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <dc:title>%(title)s</dc:title>
    <dc:identifier id="BookId">%(title)s</dc:identifier>
    <dc:creator opf:file-as="%(author)s" opf:role="aut">%(author)s</dc:creator>
   </metadata>
  <manifest>
    <item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml"/>
    %(manifest)s
  </manifest>
  <spine toc="ncx">
    %(spine)s
  </spine>
</package>'''

nav_template = '''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en-US" lang="en-US">
   <head>
      <title>EPUB 3 Navigation Document</title>
      <meta charset="utf-8"/>
      <link rel="stylesheet" type="text/css" href="css/epub.css"/>
   </head>
   <body>
      <nav epub:type="toc">
        <ol>
          %(toc)s
        </ol>
      </nav>
   </body>
</html>
'''

toc_ncx_template = '''<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" xml:lang="Zh" version="2005-1">
    <head>
        <meta name="dtb:uid" content="%(title)s" />
    <meta content="1" name="dtb:depth"/>
    <meta content="0" name="dtb:totalPageCount"/>
    <meta content="0" name="dtb:maxPageNumber"/>
  </head>
    <docTitle>
        <text>%(title)s</text>
    </docTitle>
    <navMap>
       %(toc_ncx)s
    </navMap>
</ncx>
'''


class EPubBuilder(object):
    def __init__(self, title, author, output_dir, content_dir, chapters, get_chapter_local_file = None):
        super().__init__()

        self.title_ = title
        self.output_dir_ = output_dir
        self.content_dir_ = content_dir
        self.chapters_ = chapters
        self.author_ = author

        if get_chapter_local_file:
            self.get_chapter_local_file_ = get_chapter_local_file
        else:
            self.get_chapter_local_file_ = lambda file: file

    def build(self):
        epub_file = Path(self.output_dir_) / self.title_
        epub_file = epub_file.with_suffix(".epub")

        epub = zipfile.ZipFile(str(epub_file), 'w', zipfile.ZIP_DEFLATED)

        # The first file must be named "mimetype"
        epub.writestr("mimetype", "application/epub+zip")

        epub.writestr("META-INF/container.xml", idx_data)

        manifest = ""
        spine = ""
        toc = ""
        toc_ncx = ""

        # Write each HTML file to the ebook, collect information for the index
        for i, html in enumerate([Path(self.content_dir_) / self.get_chapter_local_file_(x[1]) for x in self.chapters_]):
            if not html.exists():
                continue

            basename = os.path.basename(html)
            manifest += '<item id="file_%s" href="OEBPS/%s" media-type="application/xhtml+xml"/>' % (
                i+1, basename)
            manifest += '\n'
            spine += '<itemref idref="file_%s" />' % (i+1)
            spine += '\n'
            toc += '<li><a href="%s">OEBPS/%s</a></li>\n' % (
                basename,
                self.chapters_[i][0])
            toc_ncx += '<navPoint id="s%s" playOrder="%s"><navLabel><text>%s</text></navLabel><content src="OEBPS/%s"/></navPoint>\n' % (
                i+1,
                i+1,
                self.chapters_[i][0],
                basename)

            epub.write(html, 'OEBPS/'+basename)

        # Finally, write the index
        epub.writestr('content.opf', index_tpl % {
            'manifest': manifest,
            'spine': spine,
            'title': self.title_,
            'author': self.author_,
        })

        #epub.writestr('nav.xhtml', nav_template % {'toc': toc})
        epub.writestr('toc.ncx', toc_ncx_template % {
            'toc_ncx': toc_ncx,
            'title': self.title_
        })
