"""
fetch manga from goodmanga.net. 
"""

from HTMLParser import HTMLParser

import urllib2
import urllib

import re

prefix = 'http://www.goodmanga.net/'

def find(what, where):
    """find an attribute in a list"""
    try:
        return next(x[1] for x in where if x[0] == what )
    except StopIteration:
        return None


def urlopen(url, **kwargs):
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = { 'User-Agent' : user_agent }
    req = urllib2.Request(url, headers=headers)

    retry = kwargs.get('retry', 2)

    for i in xrange(retry):
        try:
            return urllib2.urlopen(req)
        except Exception, e:
            print 'error:', e
    raise Exception, e

def urlretrieve(url, filename, **kwargs):

    with open(filename, 'w') as f:
        f.write( urlopen(url, **kwargs).read() )


def get(manga, chapter):

    print 'fetching "{0}" chapter: {1}'.format(manga, chapter)
    
    class Parser(HTMLParser):
        """
        extract img/next links from html
        """

        def __init__(self):
            HTMLParser.__init__(self)
            self.stack = []

            self.img = None
            self.next = None
            self.link = None


        def handle_starttag(self, tag, attrs):
            if tag == 'a':

                id = find('id', self.stack[-1][1])

                if id and id == 'manga_viewer':
                    href = find('href', attrs)
                    self.next = href
                    self.link = (tag, attrs)

            if tag == 'img':
                if self.stack[-1] == self.link:
                    src = find('src', attrs)
                    self.img = src

            self.stack.append( (tag, attrs) )

        def handle_endtag(self, tag):
            del self.stack[-1]

        def handle_data(self, data):
            pass


    def infos(url):
        """download and extract infos from url"""

        response = urlopen(url)
        html = response.read()

        parser = Parser()
        parser.feed(html)

        return parser

    def download(url, filename):
        """download picture"""

        if not os.path.isfile(filename):
            try:
                print 'downloading', url
                urlretrieve (url, filename)
            except:
                try:
                    os.remove( filename )
                except OSError:
                    pass

                raise
        else:
            print 'skipping', url, '({} exists)'.format(filename)

    import os


    def mkdir(manga, chapter):
        """create output directories"""

        outdir = manga + '/' + str(chapter)

        try:
            os.makedirs( outdir )
        except OSError:
            pass

        return outdir


    outdir = mkdir( manga, chapter )

    first = prefix + manga + '/chapter/' + str(chapter)
    url = first

    while url:
        i = infos(url)

        basename = i.img.split('/')[-1].split('.')

        head = basename[0].zfill(2)
        tail = basename[1:]

        filename = outdir + '/' + '.'.join([head] + tail)

        download(i.img, filename)

        url = i.next
        if not re.match(first, url):
            # end of chapter
            break


    return outdir

def chapters(manga):
    
    class Parser(HTMLParser):
        """
        extract chapter list
        """

        def __init__(self):
            HTMLParser.__init__(self)
            self.select = None

        def handle_starttag(self, tag, attrs):
            if tag == 'select' and find('name', attrs) == 'chapter_select': 
                self.select = (tag, attrs)
                self.chapters = []
                
            elif tag == 'option' and self.select:
                value = find('value', attrs)

                if value:
                    chapter = int( value.split('/')[-1] )
                    self.chapters.append( chapter )

                
        def handle_endtag(self, tag):
            if tag == 'select' and self.select:
                self.select = None


    # parse first chapter
    url = prefix + manga + '/chapter/1'
    try:
        response = urlopen(url)

        # req = urllib2.Request(url)
        # req.add_header('Referer', prefix)
        # response = urllib2.urlopen(req)
                
        html = response.read()

        parser = Parser()
        parser.feed(html)

        return parser.chapters

    except:
        print 'error opening "{}"'.format(url)
        raise
                
if __name__ == '__main__':
    import sys
    
    manga = sys.argv[1]
    chapter = int(sys.argv[2])

    get(manga, chapter)
