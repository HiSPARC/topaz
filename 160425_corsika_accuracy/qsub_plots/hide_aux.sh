#!/usr/bin/env bash

# Hide auxiliary LaTeX output
if [[ "$OSTYPE" == "darwin"* ]]; then
    for i in *.{tex,out,log,aux,toc,bbl,dvi,blg,synctex.gz,fdb_latexmk,bcf,fls,run.xml,tdo,auxlock,pyg};
        do chflags hidden $i;
    done

    for i in */*.aux;
        do chflags hidden $i;
    done

    for i in tikz/*.{dpth,md5,run.xml,log};
        do chflags hidden $i;
    done

    for i in _minted*;
        do chflags hidden $i;
    done
fi
