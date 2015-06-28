#!/usr/bin/python

from PIL import Image
import urllib, StringIO
import os.path, errno
from Config import Config

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


#Loads several images from Google Maps servers, then stitches them together into a super image
def downloadImages( geoGrid, outputDir, shared ):
    config = Config.Instance().getConfig()

    key = config['imagery']['apiKey']

    mkdir_p(outputDir)
    xrows, ycols = geoGrid.getSubimageRowsColumns()
    print( "Number of images: {:d} x {:d} = {:d}".format( xrows, ycols, ycols*xrows))

    dx, dy = geoGrid.globalGrid.getSubimagePixelCountUnique()
    print "image size: ", dx, dy

    xwidthplus, yheightplus = geoGrid.globalGrid.getSubimagePixelCountFull()

    for x, y in geoGrid:
        lat,lon = geoGrid.localSubimageIndexToLatLon( x, y )
        imfilename = outputDir + "{:02d}_{:f}_{:f}.png".format( geoGrid.zoom, lat, lon )
        added = False

        if not os.path.isfile( imfilename ):
            position = ','.join((str(lat), str(lon)))

            urlparams = urllib.urlencode({'center': position,
                                          'zoom': str(geoGrid.zoom),
                                          'size': '%dx%d' % (xwidthplus, yheightplus),
                                          'maptype': 'satellite',
                                          'sensor': 'false',
                                          'scale': 1,
                                          'key': key})
            url = 'http://maps.google.com/maps/api/staticmap?' + urlparams

            f=urllib.urlopen(url)
            im=Image.open(StringIO.StringIO(f.read()))
            im.save( imfilename );
            added = True

        #Give status update
        mutex = shared["printMutex"]
        mutex.acquire()
        shared["totalProcessed"].value += 1

        if shared["totalToDo"].value < 0:
            shared["totalToDo"].value = geoGrid.getTotalCount()

        status = "Completed"
        if( False == added ):
            status = "Skipped"

        pct = 100. * shared["totalProcessed"].value / shared["totalToDo"].value
        print "{:9s} {:3.0f}% ({:6d} of {:6d}). (x:{:3d}, y:{:3d}, file:{}".format( status, pct, shared["totalProcessed"].value, shared["totalToDo"].value, x, y, imfilename )
        mutex.release()

