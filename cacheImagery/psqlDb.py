#! /usr/bin/python
from Config import Config
import os

def psqlDb():

    data = Config.Instance().getConfig()

    #Attach to the database
    cmd  = "psql {} -h {} -U {}".format( data['dbname'], data['host'], data['nominal']['un'])
    print "Command: {}".format( cmd )
    os.system( cmd )

#Main program
if __name__ == "__main__":
    psqlDb()
