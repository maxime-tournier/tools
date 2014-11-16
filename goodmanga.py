"""
fetch manga from goodmanga.net. 
"""

from HTMLParser import HTMLParser

import urllib2
import urllib

import re
import sys

manga = sys.argv[1]
chapter = int(sys.argv[2])


prefix = 'http://www.goodmanga.net/'

def find(what, where):
    """find an attribute in a list"""
    try:
        return next(x[1] for x in where if x[0] == what )
    except StopIteration:
        return None


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


def fetch_infos(url):
    """download and extract infos from url"""
    
    response = urllib2.urlopen(url)
    html = response.read()

    parser = Parser()
    parser.feed(html)

    return parser
    
def download(url, filename):
    """download picture"""

    if not os.path.isfile(filename):
        try:
            print 'downloading', url
            urllib.urlretrieve (url, filename)
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
    infos = fetch_infos(url)

    basename = infos.img.split('/')[-1].split('.')

    head = basename[0].zfill(2)
    tail = basename[1:]
    
    filename = outdir + '/' + '.'.join([head] + tail)

    download(infos.img, filename)

    url = infos.next
    if not re.match(first, url):
        # end of chapter
        break
    
