#!/usr/bin/env bash

for file in *.pdf; do pdfcrop --margins 5 $file $file.tmp; mv -f $file.tmp $file; done;
