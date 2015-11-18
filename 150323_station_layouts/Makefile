.PHONY: all distclean clean

TEXFILES=$(wildcard *.tex)

all:
	for file in $(TEXFILES); do \
		latexmk -quiet -pdf $$file; \
		pdfcrop $${file%%.tex}.pdf $${file%%.tex}.pdf; \
	done;

distclean:
	latexmk -quiet -C *.tex;

clean:
	latexmk -quiet -c *.tex;
