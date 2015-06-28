#!/usr/bin/python

from geographiclib.geodesic import Geodesic
import dfdbCommon
import psycopg2
import psycopg2.extras
from Config import Config
import math
import copy

#Estimates the size of a pixel at a specific location
def markDuplicates():

    conn = dfdbCommon.connectToDb()
    cur = conn.cursor( cursor_factory=psycopg2.extras.DictCursor )

    dupDistance = Config.Instance().getConfig()['detecting']['duplicates']['distance']

    #Save the picture
    sqlCmd = 'SELECT field.fieldid, location.lat, location.lon, field.angle ' \
             'FROM field ' \
             'NATURAL JOIN location '\
             'WHERE field.duplicateId IS NULL;'
    cur.execute( sqlCmd )

    fields = cur.fetchall()
    allDupKeys = []
    origs = 0
    for idxA, fieldA in enumerate(fields):        
        
        # If this field was already analyzed, skip
        if( fieldA['fieldid'] not in allDupKeys):
            dupKeys = [fieldA['fieldid']]
            dupAngs = [fieldA['angle']] 
            for fieldB in fields[idxA+1:]:
                
                # If this field was already analyzed, skip
                if( fieldB['fieldid'] not in allDupKeys):

                    #Measur ethe dstiance between the fields
                    dist = Geodesic.WGS84.Inverse( \
                            fieldA['lat'], fieldA['lon'], \
                            fieldB['lat'], fieldB['lon'])["s12"]

                    #then if that distance is small, mark it as a duplicate field
                    if( dist < dupDistance ):
                        dupKeys.append( fieldB['fieldid'])
                        dupAngs.append(fieldB['angle'])
            origs += 1
            allDupKeys.extend( dupKeys )
            
            #Get average of angles
            avgAng = calculateAverageAngleD( dupAngs )

            if len(dupAngs) == 1:
                print "({:3d}/{:3d}) Unique key: {:d}".format( origs, len(allDupKeys), dupKeys[0] )
            else:
                print '({:3d}/{:3d}) Duplicates detected: avg {:5.1f}; Keys: {}; dupAngs: {}'.format( origs, len(allDupKeys), avgAng, dupKeys, dupAngs )

                #Create a new field with average angle, if it doesn't exist
                #Mark duplicates in database
                updKeys = copy.copy( dupKeys)
                if( int( avgAng ) in dupAngs ):
                    idx = map(int,dupAngs).index(int(avgAng))
                    mainKey = dupKeys[ idx ]
                    updKeys = copy.copy( dupKeys)
                    del updKeys[idx]
                else:
                    #Save the field
                    cur.execute("INSERT INTO field(locationId, fieldSize, angle) "\
                             '  SELECT locationId, fieldSize, %s FROM field ' \
                             '  WHERE fieldId = %s '
                             'RETURNING fieldId;', (avgAng, dupKeys[0]) )
                    mainKey = cur.fetchall()[0][0]
                sqlCmd = cur.mogrify( 'UPDATE field ' \
                             'SET duplicateId = %s ' \
                             'WHERE fieldId IN (', (mainKey,) )

                constraints = ', '.join( cur.mogrify( "%s", (x,)) for x in updKeys )
                cur.execute( sqlCmd + constraints + ");" )
    conn.commit()
        
def calculateAverageAngleD( anglesD ):
    sumCos = 0.
    sumSin = 0.
    count = len(anglesD)

    for angleD in anglesD:
        sumSin += math.sin( math.radians(angleD) )
        sumCos += math.cos( math.radians(angleD) )

    avgD = math.degrees( math.atan2( sumSin / count, sumCos / count ) )

    if( avgD < 0 ):
        avgD += 360

    return avgD;


if __name__ == "__main__":
    markDuplicates();
