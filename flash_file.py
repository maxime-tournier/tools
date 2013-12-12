# display symbolic links used by flash plugin, filtered by file
# type. use it to open/copy flash videos, for example.

# TODO add argparse flags to configure filter

import os
from subprocess import Popen, PIPE

def popen( cmd ):
    return Popen(cmd, stdout = PIPE).stdout.read()

proc = popen(['pgrep', '-f', 'flash']).split('\n')[0]

input = '/proc/' + proc + '/fd/*'

filter = 'MPEG'

matches = Popen( 'file -L ' + input + ' | grep ' + filter, shell=True, stdout = PIPE ).stdout.read().split('\n')

res = [ mi.split(':')[0] for mi in matches[:-1]]

for i in res:
    print i





