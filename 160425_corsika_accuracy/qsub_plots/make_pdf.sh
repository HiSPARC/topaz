#!/usr/bin/env bash

latexmk -pdf -quiet *.tex

./hide_aux.sh
./crop_pdf.sh
