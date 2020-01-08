# Scripts to generate Shattered PoCs via pdfLaTeX


1. Run `mergeJPG.py` on 2 JPG of the same dimensions and colorspace.

```
./mergeJPG.py yes.jpg no.jpg 612 612 0
```

It will create a merged JPG with the 2 data, and a prefix PDF file.

2. Compile the PDFLaTeX file normally

```
pdflatex main
```

3. Run `fixPDF.py` on the generated PDF

```
./fixPDF.py main.pdf
```
