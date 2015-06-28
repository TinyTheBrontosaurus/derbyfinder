#!/bin/bash

for(( i = 0; i < 100; i+=5))
do
    printf -v ipad "%03d" $i
    git mv rotated_${i}_best.xml rotated_${ipad}_best.xml
    git mv rotated_${i}_all.xml rotated_${ipad}_all.xml
done
