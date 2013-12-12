# transcode mp3 and copy covers. i use this to save space on my
# android phone :)

import fnmatch
import argparse
import os
import subprocess

parser = argparse.ArgumentParser(description='batch transcode mp3')

parser.add_argument('-i', help='Input directory', required=True, action = 'append' )
parser.add_argument('-o', help='Output directory', required=True)
parser.add_argument('-b', help='Bitrate', required=False)

args = vars(parser.parse_args())

bitrate = '160k'
if args['b']: 
    bitrate = args['b']

input = args['i']
output = args['o']

# songs
songs = []

for i in input:
    for root, dirnames, filenames in os.walk(i):
        for filename in fnmatch.filter(filenames, '*.mp3'):
            songs.append(os.path.join(root, filename))

for i in songs:
    dir = os.path.dirname(i)
    out_dir = output + '/' + dir
    
    subprocess.call(['mkdir', '-p', out_dir])

    o = output + '/' + i
    cmd = ['avconv', '-i', i, '-ab', bitrate, o]
    print ' '.join(cmd)
    subprocess.call( cmd )
    
    
# covers 
covers = []
for i in input:
    for root, dirnames, filenames in os.walk(i):
        for filename in fnmatch.filter(filenames, '*.jpg'):
            covers.append(os.path.join(root, filename))

for i in covers:
    subprocess.call(['cp', '-v', i, output + '/' + i ] )

print 'done.'
