#!/bin/bash

#Every 30 degrees is a new prime dataset
for(( angle = 0; angle < 331; angle += 30 ))
do
    printf -v angleprint "%03d" $angle
    OUTFILE=prime${angleprint}.xml
    echo "Angle $angle to $OUTFILE"
    cat best.hdr > $OUTFILE
    #Each prime dataset uses 60 degrees worth of data; 30 degrees on either side
    for((imdangle = -30; imdangle <= 30; imdangle += 5 ))
    do
	fileAngleT=$((angle + imdangle))

	if [ $fileAngleT -lt 0 ]; then
	    fileAngle=$((fileAngleT + 360))
	elif [ $fileAngleT -gt 359 ]; then
	    fileAngle=$((fileAngleT - 360))
	else
	    fileAngle=$fileAngleT
	fi
	#Output for the specific angle
	cat rotated_${fileAngle}_best.xml | tail -n +7 | head -n -2 >> $OUTFILE
    done
    cat best.ftr >> $OUTFILE
done
