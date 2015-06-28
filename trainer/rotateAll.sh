#!/bin/bash

for (( angle=5; angle <= 356; angle += 5 ))
do
    echo $angle degrees!
    ./build/imglab --rotate $angle all.xml
done
