"""
take a picture directory and make a cbz from it
"""

import cv2
import os
import numpy as np
import tempfile
import subprocess


def cbz( directory ):
    # optimized for kobo glo
    resolution = (768, 1024)

    listdir = (os.path.join(directory, f) for f in os.listdir(directory))
    files = (f for f in listdir if os.path.isfile(f))

    # grayscale threshold, set large to keep color images
    threshold = 10

    tmpdir = tempfile.mkdtemp()
    tmpfiles = []

    try:
        for f in files:
            image = cv2.imread( f )
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            saturation = hsv[:, :, 1]
            mean = np.mean(saturation)

            grayscale = mean <= threshold

            if grayscale:

                height, width = image.shape[:2]

                # rotate landscape
                if width > height:
                    image = np.rot90(image)
                    height, width = image.shape[:2]

                # scale
                image = cv2.resize( image, resolution,
                                    interpolation = cv2.INTER_AREA )

                basename = os.path.split(f)[-1]

                tmp = os.path.join(tmpdir, basename)
                cv2.imwrite(tmp, image)
                tmpfiles.append( tmp )

        cbz = directory + '.cbz'
        subprocess.call(['zip', '-9', '-j', cbz] + tmpfiles)

        return cbz
    
    finally:
        for f in tmpfiles:
            os.remove( f )
        os.rmdir( tmpdir )


if __name__ == '__main__':
    import sys

    cbz( sys.argv[1] )
