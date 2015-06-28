import psycopg2
import json
from Config import Config


#Return a connection to the database
def connectToDb():
    try:
        config = Config.Instance().getConfig()
        cmd = "dbname='{}' host='{}' user='{}' password='{}'" \
                .format( config["dbname"], config["host"], config["nominal"]["un"], config["nominal"]["pw"] )
        conn = psycopg2.connect( cmd )
    except:
        print "I am unable to connect to the database"
        raise

    return conn
