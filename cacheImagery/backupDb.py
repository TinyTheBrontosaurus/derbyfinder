#!/usr/bin/python

#Backup the database

from Config import Config
import os

def backupDb():

    config = Config.Instance().getConfig()

    cmd = "pg_dump --set ON_ERROR_STOP=on {} --single-transaction -U {} > {}".format( config['dbname'], config["nominal"]['un'], config['backupFile'])
    os.system( cmd )

#Main program
if __name__ == "__main__":
    backupDb()
