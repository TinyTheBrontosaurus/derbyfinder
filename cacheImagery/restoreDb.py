#!/usr/bin/python

#Restore the database

from Config import Config
import os

def restoreDb():

    config = Config.Instance().getConfig()

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

    #Do the restoration
    cmd = "psql {} -U {} < {} > /dev/null".format( config['dbname'], config["nominal"]['un'], config['backupFile'])
    os.system( cmd )

    #Note the following errors can be ignored
    #ERROR:  must be owner of extension plpgsql
    #WARNING:  no privileges could be revoked for "public"
    #WARNING:  no privileges could be revoked for "public"
    #WARNING:  no privileges were granted for "public"
    #WARNING:  no privileges were granted for "public"


#Main program
if __name__ == "__main__":
    restoreDb()
