#!/usr/bin/env python


import PySide
from PySide.QtGui import *
from PySide.QtCore import *

import sys

app = QApplication(sys.argv)

win = QMainWindow()

wid = QWidget()
lay = QVBoxLayout()

label = QLabel('Enter a latex formula below:')
lay.addWidget(label)

# text input
text = QLineEdit()
lay.addWidget( text )

# pixmap
scene = QGraphicsScene()
scene.setBackgroundBrush( QBrush( Qt.gray, Qt.SolidPattern))
view = QGraphicsView(scene)


pixmap = QPixmap()

item = QGraphicsPixmapItem(pixmap)
scene.addItem(item);



lay.addWidget( view )
wid.setLayout( lay )
win.setCentralWidget( wid )

# copy
but = QPushButton('&Copy')
but.setShortcut( QKeySequence("CTRL+C"));
lay.addWidget( but )

clip = QClipboard()

def copy():
    global pixmap
    clip.setPixmap( pixmap )

but.clicked.connect( copy )

# latex
tex = \
"""\\documentclass[tightpage]{{standalone}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{mathpazo}}
\\usepackage{{color}}
\\usepackage{{varwidth}}
%
\\begin{{document}}
\\color{{blue}}
\\resizebox{{!}}{{100pt}}{{
${0}$
}}
\\end{{document}}"""

# TODO background
def rasterize( formula ):
    from subprocess import Popen, PIPE
    import tempfile
    
    pdf = tempfile.NamedTemporaryFile(suffix='.pdf')
    import os

    split = os.path.split(pdf.name)
    
    pdflatex = Popen(['pdflatex',
                      '-jobname', split[-1].split('.pdf')[0],
                      '-output-directory', split[0]], stdin = PIPE )
                     
    pdflatex.communicate( tex.format(formula) )
    pdflatex.wait()

    if pdflatex.returncode == 0:
        png = tempfile.NamedTemporaryFile(suffix='.png')
        
        convert = Popen(['convert', pdf.name, png.name])
        convert.wait()
        if convert.returncode == 0:
            return QPixmap(png.name)
    else:
        print 'error !'
        return None
        
def process():
    formula = text.text()
    global pixmap
    
    pixmap = rasterize( formula )
    if pixmap:
        item.setPixmap( pixmap )
        view.fitInView( item, Qt.KeepAspectRatio )
    
text.textChanged.connect( process )
win.show()

app.exec_()

