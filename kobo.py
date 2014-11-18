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

def manga(name, chapters = None ):
    """fetch, assemble and copy manga chapters to kobo"""

    # TODO don't redo unneeded stuff
    
    chapters = chapters or goodmanga.chapters(name)[-1:]
    
    for c in chapters:
        folder = goodmanga.get( name, c )
        filename = cbz.cbz( folder )

        basename = os.path.split(filename)[-1]

        destdir = path()
        destfile = os.path.join(destdir, name + '.' + basename)
        
        subprocess.call(['cp', '-v', filename, destfile])


if __name__ == '__main__':

    import sys

    name = sys.argv[1]

    if len(sys.argv) > 2:
        chapters = map(int, sys.argv[2:])
    else:
        chapters = None
        
    manga( name, chapters )
    
        
