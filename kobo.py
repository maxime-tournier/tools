"""
kobo scripts, mostly for manga scans assembly

"""

import goodmanga
import cbz
import os

import subprocess

def path():
    """kobo mountpoint"""
    # TODO check presence, make it portable, etc
    return '/Volumes/KOBOeReader'

def manga(name, chapters ):
    """fetch, assemble and copy manga chapters to kobo"""

    # TODO don't redo unneeded stuff
    
    for c in chapters:
        # folder = os.path.join(name, str(c))
        folder = goodmanga.get( name, c )
        filename = cbz.cbz( folder )

        basename = os.path.split(filename)[-1]

        destdir = path()
        destfile = os.path.join(destdir, name + '.' + basename)
        
        subprocess.call(['mv', '-v', filename, destfile])


if __name__ == '__main__':

    def parse_args():
        import argparse

        parser = argparse.ArgumentParser(description='put stuff on your kobo !')
        parser.add_argument('--manga', help='fetch, assemble and copy a manga')
        parser.add_argument('--chapters', default = None, type = int, nargs = '+',
                            help='manga chapter, fetch last chapter if omitted')
        
        return parser.parse_args()

    args = parse_args()
    
    name = args.manga
    chapters = args.chapters or goodmanga.chapters(name)[-1:]

    print chapters
    
    manga( name, chapters )
    
        
