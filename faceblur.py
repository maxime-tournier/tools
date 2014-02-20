#!/usr/bin/env python

import numpy as np

import cv
import cv2

import subprocess

help_message = '''
usage: facedetect.py [--cascade <cascade_fn>] [--nested-cascade <cascade_fn>] [input image] [output image]
'''

def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

if __name__ == '__main__':
    import sys, getopt
    # print help_message

    args, tmp = getopt.getopt(sys.argv[1:], '', ['cascade=', 'nested-cascade='])

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
    nested = cv2.CascadeClassifier(nested_fn)

    # make image
    img = cv2.imread(src);
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    rects = detect(gray, cascade)

    vis = img.copy()
    draw_rects(vis, rects, (0, 255, 0))

    ops = ''

    for x1, y1, x2, y2 in rects:
        roi = gray[y1:y2, x1:x2]
        vis_roi = vis[y1:y2, x1:x2]
        subrects = detect(roi.copy(), nested)
        # print "subrects:", subrects
        draw_rects(vis_roi, subrects, (255, 0, 0))

        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        sx, sy = x2 - x1, y2 - y1
        
        ops += '-draw "ellipse {0},{1} {2},{3} 0,360"'.format(cx, cy, sx /2 , sy / 2)

    # 
    ratio = 10

    cmd =  ['convert', src,  
            '\( +clone -scale {0}%  -scale {1}% \)'.format(100.0 / float(ratio), 100 * float(ratio)),
            '\( +clone -gamma 0 -fill white ' + ops + ' -blur 10x4 \)',
            '-composite',  dst]

    subprocess.call( ' '.join(cmd), shell = True  )

