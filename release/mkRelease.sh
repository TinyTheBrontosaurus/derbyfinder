#! /bin/bash

if [ "$#" -ne 0 ]; then
   RELEASE_NUM=`cat ../version.txt`
   RELEASE_TAG=release_$RELEASE_NUM
else
   RELEASE_NUM='master'
   RELEASE_TAG=$RELEASE_NUM
fi

PRODUCT_NAME=DerbyFinder
OUTFILE=${PRODUCT_NAME}_$RELEASE_NUM.tgz
ROOT_DIR=${PRODUCT_NAME}_$RELEASE_NUM
TMPOUTFILE=$OUTFILE.tmp
REPO='http://enelson@stash.enesimplicity.com/scm/derby/derbyfinder.git'


echo -n "Creating release for tag '$RELEASE_TAG' into $OUTFILE..."


git archive $RELEASE_TAG --remote=$REPO | gzip > $TMPOUTFILE

mkdir $ROOT_DIR
cd $ROOT_DIR
tar -zxf ../$TMPOUTFILE
cd ..
rm $TMPOUTFILE
tar czf $OUTFILE $ROOT_DIR
rm -r $ROOT_DIR

echo "done."
