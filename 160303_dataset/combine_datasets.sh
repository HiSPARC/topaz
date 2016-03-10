#!/usr/bin/env bash

cd ~/Datastore/dataset/

for i in {501..511}; do
    echo Copying $i
    ptrepack --complevel=1 --complib=blosc:zlib dataset_s${i}_110601_160201.h5:/s${i} dataset_sciencepark_stations_110601_160201.h5:/s${i}
done

h5ls dataset_sciencepark_stations_110601_160201.h5
