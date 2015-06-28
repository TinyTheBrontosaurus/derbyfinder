#!/usr/bin/python

import dlib
import re
import os
from GmapsStitchedGeoGrid import GmapsStitchedGeoGrid
from GmapsLocalGeoGrid import GmapsLocalGeoGrid
import dfdbCommon
import psycopg2.extras
import multiprocessing
import threading
from Config import Config
from skimage import io
from skimage.viewer import ImageViewer
from PIL import Image

class FieldDetector(object):

    def __init__(self):
        self._file = []
        self._angle = []
        self._size = []
        self._detector = []
        self._rawDetections = []
        self._originId = []

        # List all files. Only take ones that match "^prime(\d{3}).xml.svm"
        config = Config.Instance().getConfig()

        sourcedir = config["detecting"]["folder"]
        svmre = re.compile( "^prime(\d{3}).xml.svm" )
        allfiles = os.listdir(sourcedir)
        for filename in allfiles:
            svmrematch = svmre.match( filename )
            if svmrematch:
                fullpath = sourcedir + filename
                print "Loading {}".format( fullpath )
                self._file.append( fullpath )
                self._angle.append( int(svmrematch.group(1)))
                self._detector.append( dlib.fhog_object_detector(str(fullpath)))

    def checkImage(self, img):
        allDets = []
        #If its PIL, save and reopen as skimage
        if( isinstance( img, Image.Image )):
            tmpfile = "{}/tmp{:d}-{:d}.png".format( Config.Instance().getTempDir(), os.getpid(), threading.current_thread().ident )
            img.save( tmpfile)
            img = io.imread( tmpfile)


        if False:
            viewer = ImageViewer(img)
            viewer.show()

        for detector in self._detector:
            dets = detector(img)
            allDets.append( dets )

        self._rawDetections = allDets



    def getRawDetectionCount(self):
        count = 0

        for dets in self._rawDetections:
            count += len(dets)

        return count

    def getRawDetections(self):
        return self.rawDetections

    def printRawDetections(self, geoGrid, win = [] ):

        print "Number detected: {}".format(self.getRawDetectionCount())

        for idx, dets in enumerate(self._rawDetections):
            if win != [] :
                win.add_overlay(dets)
            for d in dets:
                fieldLat, fieldLon = geoGrid.toLatLon( d )
                print("Detection @{:3.0f} deg: (l,l)={:.6f}, {:.6f} Left: {} Top: {} Right: {} Bottom: {}".format(
                    self._angle[idx], fieldLat, fieldLon, d.left(), d.top(), d.right(), d.bottom()))

    def saveToDb( self, filename, lat, lon, geoGrid ):
        conn = dfdbCommon.connectToDb()
        cur = conn.cursor( cursor_factory=psycopg2.extras.DictCursor )

        #Save the picture
        sqlCmd = "INSERT INTO picture(filename, lat, lon, zoom ) VALUES ( '{}', {:.6f}, {:.6f}, {:d} ) RETURNING pictureid;".format( filename, lat, lon, geoGrid.localGrid.zoom )
        cur.execute( sqlCmd )

        pictureId = cur.fetchall()
        pictureId = pictureId[0][0]

        #Save the detections
        for idx, dets in enumerate(self._rawDetections):
            for d in dets:
                fieldLat, fieldLon = geoGrid.centroidToLatLon( d )

                fieldSize = geoGrid.getBoxSizeMeters( d )[0]

                #Save the location
                sqlCmd = "INSERT INTO location(lat, lon) VALUES( {:.6f}, {:.6f} ) RETURNING locationid;".format( fieldLat, fieldLon)
                cur.execute( sqlCmd );
                locationId = cur.fetchall()
                locationId = locationId[0][0]

                #Save the field
                sqlCmd = "INSERT INTO field(locationId, angle, fieldSize, pictureId, good) VALUES( {}, {:d}, {:.1f}, {}, NULL);".format(locationId, self._angle[idx], fieldSize, pictureId)
                cur.execute(sqlCmd)

                #Create a travel cost
                sqlCmd = "INSERT INTO travelcost( originLocationId, destLocationId ) VALUES( {}, {} );".format( self._originId, locationId );
                cur.execute(sqlCmd)

        conn.commit()

def saveOriginToDb(lat, lon):
    conn = dfdbCommon.connectToDb()
    cur = conn.cursor( cursor_factory=psycopg2.extras.DictCursor )

    #Create a location for the origin
    sqlCmd = "INSERT INTO location( lat, lon ) VALUES( {:.6f}, {:.6f} ) RETURNING locationid;".format( lat, lon );
    cur.execute(sqlCmd)
    originId = cur.fetchall();
    originId = originId[0][0];

    conn.commit();

    return originId

def runDetector( shared, threadId = 0, threadCount = 1 ):

    config = Config.Instance().getConfig()

    rawDir = config['imagery']['folder']

    detector = FieldDetector()

    detector._originId = shared["originId"]

    lcGrid = GmapsLocalGeoGrid( config['origin']["lat"],
                                config['origin']["lon"],
                                config['origin']['radius'],
                                config['origin']['zoom'],
                                config['origin']['stitchMag'],
                                config['origin']['stitchOverlap'])
    geoGrid = GmapsStitchedGeoGrid( lcGrid,
                                    config['origin']['stitchMag'],
                                    config['origin']['stitchOverlap'] )
    geoGrid.setThreadInfo( threadId, threadCount)

    for x, y in geoGrid:
        img, lat, lon = geoGrid.getImage( x, y, rawDir )

        detector.checkImage(img)

        detector.saveToDb( 'combined', lat, lon, geoGrid)

        #Give status update
        mutex = shared["printMutex"]
        mutex.acquire()
        shared["totalProcessed"].value += 1
        shared["totalFound"].value += detector.getRawDetectionCount()

        if shared["totalToDo"].value < 0:
            shared["totalToDo"].value = geoGrid.getTotalCount()

        pct = 100. * shared["totalProcessed"].value / shared["totalToDo"].value
        print "Completed {:3.0f}% ({:6d} of {:6d}). Found {:6d} fields. x:{:3d}, y:{:3d}".format( pct, shared["totalProcessed"].value, shared["totalToDo"].value, shared["totalFound"].value, x, y )
        mutex.release()

def worker( threadId, threadCount, shared):
    runDetector( threadId = threadId, threadCount = threadCount, shared = shared)

def threadedDetector( ):

    config = Config.Instance().getConfig()

    lat = config['origin']['lat']
    lon = config['origin']['lon']

    #False to use threads, which is slower but easier to debug than processes
    runmode = 'release'
    if Config.Instance().inDebugMode():
        runmode = 'debug'
    useProcesses = ( config['detecting'][runmode]['useProcesses'].lower() in ("yes", "true", "t", "1", "y" ) )
    threadCount = config['detecting'][runmode]['threadCount']

    if( useProcesses ):
        if( threadCount > 1 ):
            concurrencyType = 'processes'
        else:
            concurrencyType = 'process'
    else:
        if( threadCount > 1 ):
            concurrencyType = 'threads'
        else:
            concurrencyType = 'thread'

    print "Running using {:d} {}".format( threadCount, concurrencyType )

    shared = {}
    shared["originId"] = saveOriginToDb( lat, lon )

    #Processes
    shared["printMutex"] = multiprocessing.Lock()
    shared["totalProcessed"] = multiprocessing.Value('i', 0)
    shared["totalFound"] = multiprocessing.Value('i', 0)
    shared["totalToDo"] = multiprocessing.Value('i', -1)

    threads = []

    for threadId in range(threadCount):
        if( not useProcesses ):
            thread = threading.Thread( target = worker, args=(threadId, threadCount, shared) )
        else:
            thread = multiprocessing.Process( target = worker, args=(threadId, threadCount, shared) )
        threads.append(thread)
        thread.start()

    # Wait for threads to finish
    for thread in threads:
        thread.join()

    Config.Instance().cleanup()

if __name__ == "__main__":
    print "Start program"
    threadedDetector()
    print "End program"
