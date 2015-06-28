#!/bin/bash

OUTFILE=rotationsverify.txt
svm=best.svm

echo "rotation,score" > $OUTFILE

echo Angle: 0 degrees
echo -n "0," >> $OUTFILE
./build/InfieldTrainer -vf all.xml -d $svm >> $OUTFILE

for (( angle=5; angle <= 356; angle += 5 ))
do
    echo Angle: $angle degrees!
    img=rotated_${angle}_all.xml
    echo -n "$angle," >> $OUTFILE
    ./build/InfieldTrainer -vf $img -d $svm | perl -pe 'chomp' >> $OUTFILE
    echo "" >> $OUTFILE
done


