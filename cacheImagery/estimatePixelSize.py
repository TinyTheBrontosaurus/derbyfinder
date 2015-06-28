#!/usr/bin/python

from GmapsGlobalGeoGrid import GmapsGlobalGeoGrid
from geographiclib.geodesic import Geodesic
from Config import Config

#Estimates the size of a pixel at a specific location
def estimateDist( lat, lon ):

    #Radius doesn't matter, so passing in a dummy parameter
    grid = GmapsGlobalGeoGrid( 19 )

    pixelDist = 1000

    x, y = grid.latLonToGlobalPixels( lat, lon )
    latX, lonX = grid.globalPixelsToLatLon( x+pixelDist, y )
    latY, lonY = grid.globalPixelsToLatLon( x, y+pixelDist )

    distX = Geodesic.WGS84.Inverse( lat, lon, latX, lonX)["s12"]
    distY = Geodesic.WGS84.Inverse( lat, lon, latY, lonY)["s12"]

    print "Distance for {:d} pixels at {:.4f},{:.4} is {:.1f}m x and {:.1f}m Y".format( pixelDist, lat, lon, distX, distY)
    print "Distance per pixel is {:.4f}m X and {:.4f}m Y".format( distX / pixelDist, distY / pixelDist )
    print "Degree per meter is {:.12f} lat and {:.12f} lon".format( abs( latY - lat) / distY, abs( lonX - lon) / distX )

def edmain():
    config = Config.Instance().getConfig()
    lat = config['origin']['lat']
    lon = config['origin']['lon']

    estimateDist( lat, lon )

if __name__ == "__main__":
    edmain();
