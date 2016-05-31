#!/usr/bin/env bash

for i in {15.0,15.5,16.0,16.5,17.0}; do
    mkdir $i;
    cp *E_${i}*.pdf ${i}/;
done;
