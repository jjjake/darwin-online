broken-pdfs.txt.tmp:
	find . -type f -name '*.pdf' | parallel 'if ./xpdfbin-mac-3.04/bin64/pdfinfo {} 1> /dev/null 2>/dev/null; then exit;else echo {};fi' | sort > $@

clean-broken-pdfs: broken-pdfs.txt.tmp
	parallel 'rm {}' < $<

pdfs: clean-broken-pdfs
	gfind . -type f -name '*.pdf' -printf 'http://darwin-online.org.uk/converted/pdf/%P\n' | sort > got.tmp
	python scrape-it.py --pdf-urls | sort > pdf_urls.txt.tmp
	comm -23 pdf_urls.txt.tmp got.tmp > pdf_urls.txt
	gfind . -type f -name '*.tmp' -delete
	parallel 'wget -nc {}' < pdf_urls.txt

xpdf:
	wget ftp://ftp.foolabs.com/pub/xpdf/xpdfbin-mac-3.04.tar.gz
	tar xvfz xpdfbin-mac-3.04.tar.gz

init: xpdf
