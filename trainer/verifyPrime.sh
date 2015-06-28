#!/bin/bash

OUTFILE=primeverify.csv

echo -n "," > $OUTFILE

for img in rotated_*_all.xml
do
    echo -n "$img," >> $OUTFILE
done
echo "" >> $OUTFILE

for svm in prime*.svm
do
    echo -n "$svm," >> $OUTFILE
    for img in rotated_*_all.xml
    do
	echo Running $svm on $img
	./build/InfieldTrainer -vf $img -d $svm | perl -pe 'chomp' >> $OUTFILE
	echo -n "," >> $OUTFILE
    done
    echo "" >> $OUTFILE
done
