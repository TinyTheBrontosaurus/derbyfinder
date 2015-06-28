#!/usr/bin/python

#Reset the database and apply the schema

from Config import Config
import os

def resetDb():

    data = Config.Instance().getConfig()

    #Wipe the database
    cmd  = "psql -c \""
    cmd +=    "drop database if exists {};".format( data["dbname"])
    cmd += "\" {} {}".format( data["admin"]["un"], data["admin"]["pw"])
    os.system( cmd )

    #Create a new table and set its privileges.
    cmd  = "psql -c \""
    cmd +=      "create database {};".format( data["dbname"])
    cmd += "\" {} {}".format( data["admin"]["un"], data["admin"]["pw"])
    os.system( cmd )

    cmd  = "psql -c \""
    cmd +=      "GRANT ALL PRIVILEGES ON DATABASE {} TO {};".format( data["dbname"], data["nominal"]["un"] )
    cmd += "\" {} {}".format( data["admin"]["un"], data["admin"]["pw"])
    os.system( cmd )

    #Setup the tables on the new database
    cmd  = "psql -f db/schema.sql {} {}".format( data["dbname"], data["nominal"]["un"] )
    os.system( cmd )

#Main program
if __name__ == "__main__":
    resetDb()
