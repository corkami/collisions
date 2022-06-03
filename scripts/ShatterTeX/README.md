Scripts to generate Shattered PoCs via pdfLaTeX


# Explanation

The existing prefixes for Shattered (SHA-1 IPC) define the start of a standard PDF file with the header of a JPG image.

Any content can be put in the PDF.
One of the images in this document will have 2 different contents while keeping the same SHA-1.

This 'dual' image can be referenced several times, with different ratio, transformation, croppping...
This is a standard image for PDFLaTeX.

For technical details, check [article 10](https://github.com/angea/pocorgtfo/blob/master/contents/articles/18-10.pdf) in PoC||GTFO issue 0x18.


# How to

1. Run `mergeJPG.py` on 2 JPG images with the same dimensions and colorspace:

```
./mergeJPG.py yes.jpg no.jpg 612 612 0
```

It will create a merged JPG with the 2 image contents, and a prefix PDF file.

2. Compile the PDFLaTeX file normally:

```
pdflatex main
```

3. Run `fixPDF.py` to post-process the generated PDF:

```
./fixPDF.py main.pdf
```


# Example PoCs

Two simple colliding TeX documents, referencing the dual image twice:
[shattered1.pdf](shattered1.pdf) /
[shattered2.pdf](shattered2.pdf).

[PoC||GTFO issue 0x18](https://github.com/angea/pocorgtfo#0x18) is a 64 page, 30 Mb (without the attachments) document using this script. The dual image is displayed on the cover and in article 10.
