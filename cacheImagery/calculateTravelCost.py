#! /usr/bin/python
import dfdbCommon
import psycopg2.extras
import urllib
import json

class TravelCostInterface:
    
    def __init__(self):
        self.apiKey = "MISSING_API_KEy"
        self.conn = dfdbCommon.connectToDb()
        self.cur = self.conn.cursor( cursor_factory=psycopg2.extras.DictCursor )
        self.reset()


    # Add travel to this class, including the key, the orign point with its key, and the destinatin point with its key
    def addTravel(self, travelid, olat, olon, oid, dlat, dlon, did):       
        
        #Save off travel key and its index
        tindex = len( self.keys["travel"] )       
        self.keys["travel"].append( travelid )   
             
        #Save off origin key in unique key list, and its index into that list
        if( oid in self.keys["origin"]):
            oindex = self.keys["origin"].index(oid)
        else:
            oindex = len(self.keys["origin"])
            self.keys["origin"].append(oid)            
            if( oindex > 0 ):
                self.origins += '|'
            self.origins += "{},{}".format( olat, olon)
            self.count += 1
        
        #Save off destination key in unique key list, and its index into that list    
        if( did in self.keys["dest"] ):
            dindex = self.keys["dest"].index(did)
        else:
            dindex = len(self.keys["dest"])
            self.keys["dest"].append(did)    
            if( dindex > 0 ):
                self.destinations += '|'        
            self.destinations += "{},{}".format( dlat, dlon)
            self.count += 1                                
        
        self.keyIndex["travel"].append( tindex )
        self.keyIndex["origin"].append( oindex )
        self.keyIndex["dest"].append( dindex )
        
        if( self.count > 100 ):
            self.flush()
    
    # Gather up all saved locations and query google for the results. Save those results to the database
    def flush( self ):
        #Make sure there's something to send. If there isn't, this is a no op
        if( self.count > 0 ):
            #Create the URL
            url = "https://maps.googleapis.com/maps/api/distancematrix/json?&key={}&origins={}&destinations={}"\
                  .format( self.apiKey, self.origins, self.destinations )
            print( "Querying Google for {:d} locations".format( self.count))
            response = urllib.urlopen(url)
            data = json.load(response)
            
            # Parse the response
            print( "Updating the database".format( self.count))
            for idx, tindex in enumerate( self.keyIndex["travel"] ):
                oindex = self.keyIndex["origin"][idx]
                dindex = self.keyIndex["dest"][idx]
                
                tid = self.keys["travel"][tindex]
                oid = self.keys["origin"][oindex]
                did = self.keys["dest"][dindex]
                travelTime = data["rows"][oindex]["elements"][dindex]["duration"]["value"]
                travelDist = data["rows"][oindex]["elements"][dindex]["distance"]["value"]
                originAddress=data['origin_addresses'][oindex];
                destAddress=data['destination_addresses'][dindex];

                self.updateAddress( oid, originAddress)
                self.updateAddress( did, destAddress)
                
                self.updateTravelCost( tid, travelTime, travelDist )                
            
            #Reset the class
            self.reset()
            
    #Flush the buffer and commit changes to the database            
    def commit(self):
        self.flush()
        self.conn.commit()

    # Perform SQL command to update the travel costs using a primary key
    def updateTravelCost(self, id, duration, distance ):
        sqlCmd = "UPDATE travelcost " \
                 " SET travelTime = {}, "\
                 "     travelDist = {} "\
                 "WHERE travelCost.travelcostid = {}".format( duration, distance, id )
        self.cur.execute(sqlCmd)
        
    # Perform SQL command to update the address using a primary key
    def updateAddress(self, id, address):
        sqlCmd = "UPDATE location "\
             "SET address = '{}' "\
             "WHERE location.locationid = {}".format( address, id )
        self.cur.execute(sqlCmd)
    
    # Reset the class
    def reset(self):
        self.count = 0;
        self.origins = ""
        self.destinations   = ""
        # Number of addreses in current load
        self.count  = 0        
        self.keys = {}
        self.keys["origin"] = []
        self.keys["dest"]   = []
        self.keys["travel"] = []
        self.keyIndex = {};
        self.keyIndex["origin"] = []
        self.keyIndex["dest"] = []
        self.keyIndex["travel"] = []        
        

# Get all travel costs from the database and set their values
def calculateTravelCost():
    conn = dfdbCommon.connectToDb()
    cur = conn.cursor( cursor_factory=psycopg2.extras.DictCursor )
    
    # Load all the travelcosts
    sqlCmd = "SELECT travelcost.originlocationId, origin.lat, origin.lon, travelcost.destlocationid, dest.lat, dest.lon, travelcost.travelcostid FROM travelcost " \
            "JOIN location As origin ON travelcost.originLocationId = origin.locationid "\
            "JOIN location As dest ON travelcost.destLocationId = dest.locationid;"
    cur.execute(sqlCmd)
    locations = cur.fetchall()
    
    travelCost = TravelCostInterface()
    
    for location in locations:
        oid = int(location[0])
        olat = location[1]
        olon = location[2]
        did = int(location[3])
        dlat = location[4]
        dlon = location[5]
        travelid = location[6]
    
        travelCost.addTravel(travelid, olat, olon, oid, dlat, dlon, did)
    
    #Flush whatever is left
    travelCost.commit()
             
if __name__ == "__main__":
    print "Start program"
    calculateTravelCost()
    print "End program"
