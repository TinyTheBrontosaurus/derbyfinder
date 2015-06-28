#! /usr/bin/python

from PIL import Image
from geographiclib.geodesic import Geodesic


class GmapsStitchedGeoGrid(object):

    #The grid the stitch, and the magnification (integer)
    def __init__(self, localGrid, mag, overlap ):
        self.localGrid = localGrid
        self.mag = int(mag)
        self.overlap = int(overlap)

        self.localGrid.setStitchMag( mag, overlap )

        xsub, ysub = self.localGrid.getSubimageRowsColumns()
        self.xCount = (xsub - overlap ) / ( mag - overlap)
        self.yCount = (ysub - overlap ) / ( mag - overlap)

        self.threadCount = []
        self.threadId = 0


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

    def index1dToStitchedSubimageIndex(self, idx ):
        y = idx % self.yCount
        x = idx / self.yCount
        return x, y

    def stitchedSubimageIndexToLocalSubimageIndex(self, x_st, y_st):
        x_lc = x_st * (self.mag - self.overlap)
        y_lc = y_st * (self.mag - self.overlap)
        return x_lc, y_lc

    def localSubimageIndexToStitchedSubimageIndex(self, x_lc, y_lc):
        x_st = x_lc / (self.mag - self.overlap)
        y_st = y_lc / (self.mag - self.overlap)
        return x_st, y_st

    def stitchedSubimageIndexToLatLon( self, x_st, y_st ):
        x_lc, y_lc = self.stitchedSubimageIndexToLocalSubimageIndex( x_st, y_st)
        lat, lon = self.localGrid.localSubimageIndexToLatLon( x_lc, y_lc)
        return lat, lon

    def latLonToStitchedSubimageIndex(self, lat, lon ):
        x_lc, y_lc = self.localGrid.latLonToLocalSubimageIndex(lat, lon )
        x_st, y_st = self.localSubimageIndexToStitchedSubimageIndex( x_lc, y_lc)
        return x_st, y_st

    def stitchedPixelToLocalPixel(self, x_st, y_st, x_st_pix, y_st_pix):
        x_lc_0, y_lc_0 = self.stitchedSubimageIndexToLocalSubimageIndex(x_st, y_st)
        x_offset = x_st_pix / self.localGrid.globalGrid.getSubimageXPixelCountUnique()
        x_lc_pix = x_st_pix % self.localGrid.globalGrid.getSubimageXPixelCountUnique()
        y_offset = y_st_pix / self.localGrid.globalGrid.getSubimageYPixelCountUnique()
        y_lc_pix = y_st_pix % self.localGrid.globalGrid.getSubimageYPixelCountUnique()
        x_lc = x_lc_0 + x_offset
        y_lc = y_lc_0 + y_offset

        return x_lc, y_lc, x_lc_pix, y_lc_pix

    def stitchedPixelToLatLon(self, x_st, y_st, x_st_pix, y_st_pix):
        x_lc, y_lc, x_lc_pix, y_lc_pix = self.stitchedPixelToLocalPixel(x_st, y_st, x_st_pix, y_st_pix)
        x_gl, y_gl = self.localGrid.localPixelsToGlobalPixels(x_lc, y_lc, x_lc_pix, y_lc_pix)
        lat, lon = self.localGrid.globalGrid.globalPixelsToLatLon(x_gl, y_gl)
        return lat, lon

    def getPixelsPerImage(self):
        xpix_lcu, ypix_lcu = self.localGrid.globalGrid.getSubimagePixelCountUnique()
        xpix_lcr, ypix_lcr = self.localGrid.globalGrid.getSubimagePixelCountFull()

        xpix = xpix_lcu * (self.mag-1)+xpix_lcr
        ypix = ypix_lcu * (self.mag-1)+ypix_lcr
        return xpix, ypix

    def getImage(self, x_st, y_st, imgDir):
        lat,lon = self.stitchedSubimageIndexToLatLon( x_st, y_st )

        xpix_lc, ypix_lc = self.localGrid.globalGrid.getSubimagePixelCountUnique()

        xpix = xpix_lc * self.mag
        ypix = ypix_lc * self.mag

        img = Image.new("RGB", (xpix, ypix ) )

        baseX, baseY = self.stitchedSubimageIndexToLocalSubimageIndex(x_st, y_st)

        for x_i in xrange( 0, self.mag):
            for y_i in reversed(xrange( 0, self.mag )):

                subImg = self.localGrid.getImage( baseX + x_i, baseY + y_i, imgDir )[0]

                #Invert Y because image coordinate direction is different form latitude direction
                img.paste( subImg, (x_i * xpix_lc, (self.mag - y_i - 1) * ypix_lc) )

        return img, lat, lon


    def subimageIndexCount(self, x, y):
        idx = x * self.yCount + y

    def getSubimageRowsColumns( self ):
        return self.xCount, self.yCount

    #Set the 0-index thread id (id) and the total number of threads (count). Used in iteration only
    def setThreadInfo(self, tid, tcount ):
        self.threadId = tid;
        self.threadCount = tcount;

    def getIterXy(self):
        xret, yret = self.index1dToStitchedSubimageIndex(self.iterIndex)
        return xret, yret

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
            xret, yret = self.index1dToStitchedSubimageIndex(self.iterIndex)

            return xret, yret

    # Covert a dlib rectangle's centroid to a lat/lon.
    def centroidToLatLon(self, det):

        #Calculate teh centroid
        xpix, ypix = self.getPixelsPerImage()
        imgFieldCtrY = ypix - ( ( det.bottom() - det.top() ) / 2 + det.top() )
        imgFieldCtrX = ( det.right() - det.left() ) / 2 + det.left()

        #Convert to global pixels, then to lat lon
        x_st,y_st = self.getIterXy()
        lat,lon = self.stitchedPixelToLatLon(x_st, y_st, imgFieldCtrX, imgFieldCtrY)

        return lat, lon


    #Get the dimensions in meters of a dlib rectangle
    def getBoxSizeMeters(self, det ):
        x_st,y_st = self.getIterXy()
        latC,lonC = self.stitchedSubimageIndexToLatLon(x_st, y_st)
        pixC, piyC = self.localGrid.globalGrid.latLonToGlobalPixels( latC, lonC )

        #Do latitude
        pixelCountTb = abs( det.bottom() - det.top() )
        piyT = piyC + pixelCountTb / 2
        piyB = piyC - pixelCountTb / 2
        pixT = pixC
        pixB = pixC
        #Ignore the longitude return value since it's the same as lonC
        latT = self.localGrid.globalGrid.globalPixelsToLatLon(pixT, piyT)[0]
        latB = self.localGrid.globalGrid.globalPixelsToLatLon(pixB, piyB)[0]
        lonT = lonC
        lonB = lonC
        latMeters = Geodesic.WGS84.Inverse(latT, lonT, latB, lonB )
        latMeters = latMeters['s12']

        # Do longitude
        pixelCountLr = abs( det.left() - det.right() )
        pixL = pixC + pixelCountLr / 2
        pixR = pixC - pixelCountLr / 2
        piyL = piyC
        piyR = piyC
        #Ignore the latitude return value since it's the same as lonC
        latR = latC
        latL = latC
        lonR = self.localGrid.globalGrid.globalPixelsToLatLon(pixL, piyL)[1]
        lonL = self.localGrid.globalGrid.globalPixelsToLatLon(pixR, piyR)[1]
        lonMeters = Geodesic.WGS84.Inverse(latR, lonR, latL, lonL )
        lonMeters = lonMeters['s12']

        return latMeters, lonMeters
