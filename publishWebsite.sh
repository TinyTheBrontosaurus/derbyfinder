#! /bin/bash

#A proper release has no git directory, so check for it.
if [ "$#" -ne 0 ]; then
    echo "Forcing publish"
elif [ -e ".git" ]; then
   echo "This is not a valid release. Setup will not continue. -f to Force"
   exit 1
fi

WEBSITE_ROOT=/var/www/html/
WEBSITE_DIR=DerbyFinder_`cat version.txt`
WEBSITE_PATH=$WEBSITE_ROOT/$WEBSITE_DIR
WEBDATA_DIR=`pwd`/www
WEBSITE_LATEST=$WEBSITE_ROOT/DerbyFinder

#Post to the website
cd $WEBSITE_ROOT
ln -s $WEBDATA_DIR $WEBSITE_DIR
rm $WEBSITE_LATEST
ln -s $WEBSITE_PATH $WEBSITE_LATEST
chmod a+w $WEBSITE_LATEST/

echo "Website posted at $WEBSITE_PATH and $WEBSITE_LATEST"
