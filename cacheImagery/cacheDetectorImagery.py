#!/usr/bin/python

import logging
from downloadImages import downloadImages
from GmapsLocalGeoGrid import GmapsLocalGeoGrid
import threading
import multiprocessing
from Config import Config
import os
import errno

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

#Cache imagery. Location and radius determined by config file
def cacheDetectorImagery( threadId, threadCount, shared  ):
    config = Config.Instance().getConfig()

    lat = config['origin']['lat']
    lon = config['origin']['lon']
    radius = config['origin']['radius']
    zoom = config['origin']['zoom']
    mag = config['origin']['stitchMag']
    overlap = config['origin']['stitchOverlap']

    #Load the imagery
    rawDir = config['imagery']['folder']

    grid = GmapsLocalGeoGrid( lat, lon, radius, zoom, mag, overlap)
    grid.setThreadInfo(threadId, threadCount)
    downloadImages( grid, rawDir, shared )

def worker( threadId, threadCount, shared):
    cacheDetectorImagery( threadId = threadId, threadCount = threadCount, shared = shared)

def threadedCacheDetectorImagery( ):
    data = Config.Instance().getConfig()

    #False to use threads, which is slower but easier to debug than processes
    runmode = 'release'
    if Config.Instance().inDebugMode():
        runmode = 'debug'
    useProcesses = ( data['cacheImagery'][runmode]['useProcesses'].lower() in ("yes", "true", "t", "1", "y" ) )
    threadCount = data['cacheImagery'][runmode]['threadCount']

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

    threadCount = data['cacheImagery'][runmode]['threadCount']

    shared = {}
    #Processes
    shared["printMutex"] = multiprocessing.Lock()
    shared["totalProcessed"] = multiprocessing.Value('i', 0)
    shared["totalToDo"] = multiprocessing.Value('i', -1)

    #Create a bunch of threads to collect imagery
    threads = []
    for threadId in range(threadCount):
        if( useProcesses ):
            t = multiprocessing.Process( target = worker, args=(threadId, threadCount, shared) )
        else:
            t = threading.Thread( target = worker, args=(threadId, threadCount, shared) )
        threads.append(t)
        t.start()

    #Wait for them all to finish
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    threadedCacheDetectorImagery()
