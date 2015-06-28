#! /usr/bin/python


from math import log, exp, tan, atan, pi, floor

class GmapsGlobalGeoGrid(object):

    EARTH_RADIUS = 6378137
    EQUATOR_CIRCUMFERENCE = 2 * pi * EARTH_RADIUS
    INITIAL_RESOLUTION = EQUATOR_CIRCUMFERENCE / 256.0
    ORIGIN_SHIFT = EQUATOR_CIRCUMFERENCE / 2.0

    SUBIMAGE_PIXEL_COUNT = 640
    SUBIMAGE_LAT_Y_OVERLAP = 120
    SUBIMAGE_LON_X_OVERLAP = 3
    
    #Lat, Lon in degrees. Radius in meters
    def __init__(self, zoom ):
        self.zoom = zoom

    #Converts between pixels and lat/lon in degrees
    def globalPixelsToLatLon( self, px_lon, py_lat ):
        res = self.INITIAL_RESOLUTION / (2**self.zoom)
        mx_lon = floor(px_lon) * res - self.ORIGIN_SHIFT
        my_lat = floor(py_lat) * res - self.ORIGIN_SHIFT
        lat = (my_lat / self.ORIGIN_SHIFT) * 180.0
        lat = 180 / pi * (2*atan(exp(lat*pi/180.0)) - pi/2.0)
        lon = (mx_lon / self.ORIGIN_SHIFT) * 180.0
        return lat, lon

    #Converts between pixels and lat/lon in degrees
    def latLonToGlobalPixels( self, lat, lon ):
        mx_lon = (lon * self.ORIGIN_SHIFT) / 180.0
        my_lat = log(tan((90 + lat) * pi/360.0))/(pi/180.0)
        my_lat = (my_lat * self.ORIGIN_SHIFT) /180.0
        res = self.INITIAL_RESOLUTION / (2**self.zoom)
        px_lon = (mx_lon + self.ORIGIN_SHIFT) / res
        py_lat = (my_lat + self.ORIGIN_SHIFT) / res
        return px_lon, py_lat

    def globalPixelsToGlobalSubimageIndex(self, px_lon, py_lat):
        subX_lon = int( px_lon / self.getSubimageXPixelCountUnique() )
        subY_lat = int( py_lat / self.getSubimageYPixelCountUnique() )

        return subX_lon, subY_lat

    def globalSubimageIndexToGlobalPixels(self, subX_lon, subY_lat ):
        px_lon = (int(subX_lon) + 0.5) * self.getSubimageXPixelCountUnique()
        py_lat = (int(subY_lat) + 0.5) * self.getSubimageYPixelCountUnique()

        return px_lon, py_lat

    def globalSubimagePixelsToGlobalPixels(self, x_gl, y_gl, x_pix, y_pix ):
        px_lon = x_gl * self.getSubimageXPixelCountUnique() + x_pix
        py_lat = y_gl * self.getSubimageYPixelCountUnique() + y_pix

        return px_lon, py_lat

    def latLonToGlobalSubimageIndex(self, lat, lon):
        px_lon, py_lat = self.latLonToGlobalPixels( lat, lon )
        subX_lon, subY_lat = self.globalPixelsToGlobalSubimageIndex( px_lon, py_lat)
        return subX_lon, subY_lat
    def globalSubimageIndexToLatLon(self, subX_lon, subY_lat ):
        px_lon, py_lat = self.globalSubimageIndexToGlobalPixels( subX_lon, subY_lat)
        lat, lon = self.globalPixelsToLatLon(px_lon, py_lat )
        return lat, lon

    def getSubimagePixelCountFull(self):
        return self.getSubimageXPixelCountFull(), self.getSubimageYPixelCountFull()

    def getSubimagePixelCountUnique(self):
        return self.getSubimageXPixelCountUnique(), self.getSubimageYPixelCountUnique()

    def getSubimageXPixelCountFull(self):
        return self.SUBIMAGE_PIXEL_COUNT

    def getSubimageYPixelCountFull(self):
        return self.SUBIMAGE_PIXEL_COUNT

    def getSubimageXPixelCountUnique(self):
        return self.SUBIMAGE_PIXEL_COUNT - self.SUBIMAGE_LON_X_OVERLAP

    def getSubimageYPixelCountUnique(self):
        return self.SUBIMAGE_PIXEL_COUNT - self.SUBIMAGE_LAT_Y_OVERLAP

