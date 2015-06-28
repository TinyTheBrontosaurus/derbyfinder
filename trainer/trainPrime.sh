#!/bin/sh

for f in prime*.xml
do
    echo Running on $f
    ./build/InfieldTrainer -tf $f -d $f.svm --noflip
done
