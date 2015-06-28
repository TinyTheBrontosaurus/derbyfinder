#!/bin/bash

for(( angle = 5; angle < 180; angle += 5 ))
do
    printf -v angleprint "%03d" $angle
    OUTFILE=best${angleprint}.xml
        echo "Angle $angle to $OUTFILE"
    cat best.hdr > $OUTFILE
    #Output angle 0
    cat best.tmp >> $OUTFILE
    #Output all angles from 5 to the target angle
    for((imdangle = 5; imdangle < angle; imdangle += 5 ))
    do
       #Output for the specific angle
	cat best.tmp | sed -e 's/grass\//grass\/rotated_${imdangle}_/g' -e 's/dirt\//dirt\/rotated_${imdangle}_/g' >> $OUTFILE
    done
    cat best.ftr >> $OUTFILE
done
