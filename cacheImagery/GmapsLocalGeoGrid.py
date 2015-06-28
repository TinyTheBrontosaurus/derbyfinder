#! /usr/bin/python

from GmapsGlobalGeoGrid import GmapsGlobalGeoGrid
from geographiclib.geodesic import Geodesic
from PIL import Image
import os.path

class GmapsLocalGeoGrid(object):

    #Lat, Lon in degrees. Radius in meters
    def __init__(self, lat, lon, radius, zoom, stitchMag = 1, stitchOverlap = 0 ):
        self.zoom = zoom
        self.globalGrid = GmapsGlobalGeoGrid( zoom )

        lineNorth = Geodesic.WGS84.Line( lat, lon,   0 )
        lineEast  = Geodesic.WGS84.Line( lat, lon,  90 )
        lineSouth = Geodesic.WGS84.Line( lat, lon, 180 )
        lineWest  = Geodesic.WGS84.Line( lat, lon, 270 )

        posNorth = lineNorth.Position( radius )['lat2']
        posEast  = lineEast.Position( radius )['lon2']
        posSouth = lineSouth.Position( radius )['lat2']
        posWest  = lineWest.Position( radius )['lon2']

        self.x0, self.y0 = self.globalGrid.latLonToGlobalSubimageIndex( posSouth, posWest )

        xn, yn = self.globalGrid.latLonToGlobalSubimageIndex( posNorth, posEast )

        self.xCount = xn - self.x0 + 1
        self.yCount = yn - self.y0 + 1

        self.setStitchMag( stitchMag, stitchOverlap )

        self.threadId = 0
        self.threadCount = []

    def setStitchMag(self, mag, overlap ):
        #Make sure the counts are an integer multiple of the magnitude
        magPrime = mag - overlap
        xdiff = ( self.xCount % magPrime ) - overlap
        if( xdiff > 0 ):
            self.xCount += magPrime - xdiff
        elif(xdiff < 0 ):
            self.xCount += ( -xdiff )

        ydiff = ( self.yCount % magPrime ) - overlap
        if( ydiff > 0 ):
            self.yCount += magPrime - ydiff
        elif(ydiff < 0 ):
            self.yCount += ( -ydiff )


    def getTotalCount(self):
        return self.xCount * self.yCount

    def getStartIndex(self):
        startIndex = 0
        if( self.threadCount):
            startIndex = int( ( float(self.threadId) /  self.threadCount ) * self.getTotalCount() )

        return startIndex

    def getEndIndex(self):
        endIndex = self.getTotalCount()
        if( self.threadCount):
            endIndex = int( ( float(self.threadId+1) /  self.threadCount ) * self.getTotalCount() )

        return endIndex

    def index1dToLocalSubimageIndex(self, idx ):
        y = idx % self.yCount
        x = idx / self.yCount
        return x, y

    def localSubimageIndexToGlobalSubimageIndex(self, x_lc, y_lc):
        x_gl = x_lc + self.x0
        y_gl = y_lc + self.y0
        return x_gl, y_gl

    def globalSubimageIndexToLocalSubimageIndex(self, x_gl, y_gl):
        x_lc = x_gl - self.x0
        y_lc = y_gl - self.y0
        return x_lc, y_lc

    def localSubimageIndexToLatLon( self, x_lc, y_lc ):
        x_gl, y_gl = self.localSubimageIndexToGlobalSubimageIndex( x_lc, y_lc)
        lat, lon = self.globalGrid.globalSubimageIndexToLatLon( x_gl, y_gl )
        return lat, lon

    def latLonToLocalSubimageIndex(self, lat, lon ):
        x_gl, y_gl = self.globalGrid.latLonToGlobalSubimageIndex(lat, lon)
        x_lc, y_lc = self.globalSubimageIndexToLocalSubimageIndex( x_gl, y_gl )
        return x_lc, y_lc

    def localPixelsToGlobalPixels(self, x_lc, y_lc, x_lc_pix, y_lc_pix):
        x_gl, y_gl = self.localSubimageIndexToGlobalSubimageIndex( x_lc, y_lc)
        x_gl_pix, y_gl_pix = self.globalGrid.globalSubimagePixelsToGlobalPixels(x_gl, y_gl, x_lc_pix, y_lc_pix )
        return x_gl_pix, y_gl_pix

    def getImage(self, x, y, imgDir):
        lat,lon = self.localSubimageIndexToLatLon( x, y )
        imgFile = imgDir + "{:02d}_{:f}_{:f}.png".format( self.zoom, lat, lon )
        img = Image.open(imgFile)
        
        return img, lat, lon

    def getSubimageRowsColumns( self ):
        return self.xCount, self.yCount

    #Set the 0-index thread id (id) and the total number of threads (count). Used in iteration only
    def setThreadInfo(self, tid, tcount ):
        self.threadId = tid;
        self.threadCount = tcount;

    # Iterator
    def __iter__(self):
        self.iterIndex = self.getStartIndex() - 1
        return self

    #Get the next in the iterator
    def next(self):
        self.iterIndex += 1
        if (self.iterIndex >= self.getEndIndex() ):
            raise StopIteration
        else:
            xret, yret = self.index1dToLocalSubimageIndex(self.iterIndex)

            return xret, yret