#!/bin/sh

for f in *.xml
do
    echo Running on $f
    ./build/InfieldTrainer -tf $f -d $f.svm
done
