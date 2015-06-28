#!/usr/bin/python

from PIL import Image
import urllib, StringIO
from math import log, exp, tan, atan, pi, ceil
import os.path, errno
from ODSReader import ODSReader
import shutil
import math
import GmapsGlobalGeoGrid
from downloadImages import downloadImages


#Broken with geoGrid checkin
def cacheTrainingImagery():
    BaseColumns = enum(SECOND = 0, HOME = 1, FIELD_TYPE = 2)

    srcfile = os.getcwd() + "/BaseLocations.ods"

    doc = ODSReader(srcfile)

    xmlFilesOpened = []

    table = doc.getSheet("Sheet1")
    table.pop(0)
    for row in table:
        friendlyName =  row[BaseColumns.SECOND].replace(" ", "_")
        intermediateDir = "../imageryBases/01_rawTiles/"
        outDir = "../imageryBases/02_stichedImages/"
        rotateDir = "../imageryBases/03_rotated/" + row[BaseColumns.FIELD_TYPE] + "/"
        mkdir_p(intermediateDir)
        mkdir_p( outDir )
        mkdir_p(rotateDir)

        outfile = outDir + friendlyName + ".png"
        rotfile = rotateDir + friendlyName + ".png"
        xmlfile = "./" + row[BaseColumns.FIELD_TYPE] + "_gen.xml"

        FINAL_IMAGE_DIM_X = 640
        FINAL_IMAGE_DIM_Y = 640
        RAW_IMAGE_DIM_X = math.ceil(FINAL_IMAGE_DIM_X * math.sqrt(2))
        RAW_IMAGE_DIM_Y = math.ceil(FINAL_IMAGE_DIM_X * math.sqrt(2))

        #Determine the bounding box
        b2lat, b2lon = map(float, row[BaseColumns.SECOND].split(','))
        b2x, b2y = latlontopixels(b2lat, b2lon)
        hplat, hplon = map(float, row[BaseColumns.HOME].split(','))
        hpx, hpy = latlontopixels(hplat, hplon)

        ctx = (hpx + b2x) / 2
        cty = (hpy + b2y) / 2

        bbulx = ctx - ( RAW_IMAGE_DIM_X / 2 );
        bblrx = ctx + ( RAW_IMAGE_DIM_X / 2 );
        bbuly = cty + ( RAW_IMAGE_DIM_Y / 2 );
        bblry = cty - ( RAW_IMAGE_DIM_Y / 2 );

        bbullat, bbullon = pixelstolatlon(bbulx, bbuly )
        bblrlat, bblrlon = pixelstolatlon(bblrx, bblry )

        bbul = "%.6f,%.6f" % (bbullat, bbullon)
        bblr = "%.6f,%.6f" % (bblrlat, bblrlon)

        #Get the images from the server and stitch them together
        downloadImages( bbul, bblr, outfile, intermediateDir )

        #Rotate the resulting stitched image so that second base is up
        angle = math.atan2(b2y-hpy, b2x-hpx)*180/math.pi - 90
        unrot = Image.open( outfile )
        rot = unrot.rotate(-angle)
        crp = rot.crop( ( ( FINAL_IMAGE_DIM_X - RAW_IMAGE_DIM_X ) / 2,
                          ( FINAL_IMAGE_DIM_Y - RAW_IMAGE_DIM_Y ) / 2,
                          FINAL_IMAGE_DIM_X - ( FINAL_IMAGE_DIM_X - RAW_IMAGE_DIM_X ) / 2,
                          FINAL_IMAGE_DIM_Y - ( FINAL_IMAGE_DIM_Y - RAW_IMAGE_DIM_X ) / 2 ) )
        crp.save( rotfile )

        #Add the XML data
        mag = math.sqrt( (b2y-hpy)**2 + (b2x-hpx)**2 );

        height = ceil( mag * 1.65 )
        width  = height
        top    = ( FINAL_IMAGE_DIM_Y / 2 ) - ( height / 2 ) * (1 + 1. / 6.)
        left   = ( FINAL_IMAGE_DIM_X / 2 ) - ( width  / 2 )

        #Append info to existing file
        if xmlfile in xmlFilesOpened:
            xmlOut = open (xmlfile, "a")
        #Add the headers to the file. Overwrite existing info.
        else:
            xmlOut = open (xmlfile, "w")
            xmlFilesOpened.append(xmlfile)
            xmlOut.write( "<?xml version='1.0' encoding='ISO-8859-1'?>\n" )
            xmlOut.write( "<?xml-stylesheet type='text/xsl' href='image_metadata_stylesheet.xsl'?>\n")
            xmlOut.write( "<dataset>\n" )
            xmlOut.write( "<name>imglab dataset</name>\n" );
            xmlOut.write( "<comment>Created by loadImagery.py.</comment>\n" );
            xmlOut.write( "<images>\n" );

        xmlOut.write( "  <image file='%s'>\n" % (rotfile) );
        xmlOut.write( "    <box top='%d' left='%d' width='%d' height='%d'/>\n" %
                      ( top, left, width, height ))
        xmlOut.write( "  </image>\n");
        xmlOut.close();

    #Put the footers on the files
    for xmlfile in xmlFilesOpened:
        xmlOut = open( xmlfile, "a")
        xmlOut.write( "</images>\n")
        xmlOut.write( "</dataset>\n")
        xmlOut.close();

    print "Done"

if __name__ == "__main__":
    cacheTrainingImagery()
