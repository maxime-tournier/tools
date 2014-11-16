#!/usr/bin/env python

import numpy as np

import cv
import cv2

import subprocess
import math

help_message = '''
usage: facedetect.py [--cascade <cascade_fn>] [--nested-cascade <cascade_fn>] input output
'''

def detect(img, cascade):

    rects = []

    neighbors = 4

    while len(rects) == 0 and neighbors > 0:
        rects = cascade.detectMultiScale(img, 
                                         scaleFactor=1.2, 
                                         minNeighbors=3, 
                                         minSize=(64, 64), 
                                         flags = cv2.CASCADE_SCALE_IMAGE)

        neighbors -= 1

    if len(rects) == 0:
        return []

    rects[:,2:] += rects[:,:2]
    return rects

def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)


def blur(src, dst, cascade):
    # make image
    img = cv2.imread(src);
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    rects = detect(gray, cascade )

    if len(rects) == 0:
        print src, "no face detected !"

    # restore
    backup_filename = 'faces.data'
    try:
        with open(backup_filename) as f:
            from numpy import array, int32
            backup = eval( f.read() )
    except IOError:
        backup = []



    def dist(a, b):
        ca = 0.5 * np.array( [sum(a[::2]), sum(a[1::2])] )
        cb = 0.5 * np.array( [sum(b[::2]), sum(b[1::2])] )

        delta = (ca - cb)
        d = math.sqrt( delta.dot(delta) )

        return d
    
    # compare rectangles
    full = []

    epsilon = 20

    # if backup is not None and len(rects) <= len(backup):
    #     for b in backup:
    #         for r in rects:
    #             if dist(b, r) > epsilon:
    #                 full.append( b )

    # full is rects + backup if distance is more than threshold
    for i in rects:
        full.append( i )

    for b in backup:
        full.append( b )
        
        
    # cleanup
    final = []
    
    for i, ri in enumerate(full):
        ok = True
        
        for j, rj in enumerate(final):
            if dist(ri, rj) < epsilon:
                ok = False
                break
        if ok:
            final.append( ri )

    print final
            
    # save
    with open(backup_filename, 'w') as f:
        f.write( repr(final) )
        
    vis = img.copy()
    # draw_rects(vis, rects, (0, 255, 0))

    ops = ''

    scale = 1.25
    for x1, y1, x2, y2 in final:
        # print 'rect'
        # roi = gray[y1:y2, x1:x2]
        # vis_roi = vis[y1:y2, x1:x2]
        # subrects = detect(roi.copy(), nested)
        # print "subrects:", subrects
        # draw_rects(vis_roi, subrects, (255, 0, 0))

        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        sx, sy = scale * (x2 - x1), scale * (y2 - y1)
        
        ops += '-draw "ellipse {0},{1} {2},{3} 0,360" '.format(cx, cy, sx /2 , sy / 2)

    # 

    # print ops

    ratio = 16

    cmd =  ['convert', src,  
            '\( +clone -scale {0}%  -scale {1}% \)'.format(100.0 / float(ratio), 100 * float(ratio)),
            '\( +clone -gamma 0 -fill white ' + ops + ' -blur 10x4 \)',
            '-composite',  dst]

    subprocess.call( ' '.join(cmd), shell = True  )



if __name__ == '__main__':
    import sys, getopt
    # print help_message

    args, tmp = getopt.getopt(sys.argv[1:], '', ['cascade=', 'nested-cascade=', 'alt='])

    try:
        src = tmp[0]
        dst = tmp[1]
    except:
        raise

    args = dict(args)
    
    path = '/usr/local/opt/opencv/share/OpenCV/'

    cascade_fn = args.get('--cascade', path + '/haarcascades/haarcascade_frontalface_alt.xml')
    nested_fn  = args.get('--nested-cascade', path + '/haarcascades/haarcascade_eye.xml')

    cascade = cv2.CascadeClassifier(cascade_fn)

    blur(src, dst, cascade)

    
