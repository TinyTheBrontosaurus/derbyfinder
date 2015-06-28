#!/bin/bash

for(( angle = 5; angle < 181; angle += 5 ))
do
    printf -v angleprint "%03d" $angle
    OUTFILE=best${angleprint}.xml
    echo "Angle $angle to $OUTFILE"
    cat best.hdr > $OUTFILE
    #Output angle 0
    cat best.xml | tail -n +7 | head -n -2  >> $OUTFILE
    #Output all angles from 5 to the target angle
    for((imdangle = 5; imdangle <= angle; imdangle += 5 ))
    do
       #Output for the specific angle
	cat rotated_${imdangle}_best.xml | tail -n +7 | head -n -2 >> $OUTFILE
    done
    cat best.ftr >> $OUTFILE
done
