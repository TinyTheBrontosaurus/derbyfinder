#!/bin/bash

for (( angle=0; angle <= 355; angle += 5 ))
do
    echo $angle degrees!
    ./build/imglab --rotate $angle best.xml
done
