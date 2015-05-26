"""
kobo scripts, mostly for manga scans assembly

"""

import goodmanga
import cbz
import os
import glob

import subprocess
import time

def path():
    """kobo mountpoint"""
    # TODO check presence, make it portable, etc
    return '/Volumes/KOBOeReader'

def manga(name, chapters, **kwargs  ):
    """fetch, assemble and copy manga chapters to kobo"""

    # TODO don't redo unneeded stuff
    pause = kwargs.get('pause', 0)
    
    for c in chapters:
        # folder = os.path.join(name, str(c))
        folder = goodmanga.get( name, c )
        filename = cbz.cbz( folder )

        basename = os.path.split(filename)[-1]

        destdir = path()
        destfile = os.path.join(destdir, name + '.' + basename)
        
        subprocess.call(['mv', '-v', filename, destfile])
        time.sleep( pause )
        
def available(name):
    """determines which chapters to fetch"""

    filenames = [ f for f in os.listdir(path()) if f.startswith(name) ] 

    chapters = [ int(f.split('.')[1]) for f in filenames ]
    last = max(chapters)

    latest = goodmanga.chapters(name)[-1]

    return [ i + 1 for i in xrange(last, latest) ]

if __name__ == '__main__':

    def parse_args():
        import argparse

        parser = argparse.ArgumentParser(description='put stuff on your kobo !')
        parser.add_argument('--manga', help='fetch, assemble and copy a manga')
        parser.add_argument('--chapters', default = None, type = int, nargs = '+',
                            help='manga chapter, fetch available chapters if omitted')

        return parser.parse_args()

    args = parse_args()
    
    name = args.manga
    chapters = args.chapters or available(name) # goodmanga.chapters(name)[-1:]

    if not chapters:
        print 'nothing to fetch'
        
    manga( name, chapters, pause = 1 )
    
        
