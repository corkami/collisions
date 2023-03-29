<!-- pandoc -s -f gfm -t html README.md -o README.html -->

Tiny, copyright-free, PII-free collision PoCs


# MD5


## FastColl

- GIF images [md5-1.gif](md5-1.gif) / [md5-2.gif](md5-2.gif)


## UniColl

- GZip archives [md5-1.gz](md5-1.gz) / [md5-2.gz](md5-2.gz)
- JPG images
  - via UniColl [md5-1.jpg](md5-1.jpg) / [md5-2.jpg](md5-2.jpg)
  - via modified FastColl [md5-1fc.jpg](md5-1fc.jpg) / [md5-2fc.jpg](md5-2fc.jpg)
- PDF documents [md5-1.pdf](md5-1.pdf) / [md5-2.pdf](md5-2.pdf)
- PNG images
   - generic header, not 100% compatible
     - appended data [md5-1.png](md5-1.png) / [md5-2.png](md5-2.png)
     - appended data w/ correct CRCs [md5-crc1.png](md5-crc1.png) / [md5-crc2.png](md5-crc2.png)
     - synchronized comments [md5-sync1.png](md5-sync1.png) / [md5-sync2.png](md5-sync2.png)
   - specific header w/ common dimensions/colorspace [md5-s1.png](md5-s1.png) / [md5-s2.png]( md5-s2.png)
- MP4
  - generic header, 32b length (LTV) [md5-1.mp4](md5-1.mp4) / [md5-2.mp4](md5-2.mp4)
  - generic header, 64b length (TLV) [md5-l1.mp4](md5-l1.mp4) / [md5-l2.mp4](md5-l2.mp4)
  - specific header [md5-s1.mp4](md5-s1.mp4) / [md5-s2.mp4](md5-s2.mp4)

- ZIP [md5-1.zip](md5-1.zip) / [md5-2.zip](md5-2.zip)

- LZ4 archives [md5-1.lz4](md5-1.lz4) / [md5-2.lz4](md5-2.lz4)
- Zstandard archives [md5-1.zstd](md5-1.zstd) / [md5-2.zstd](md5-2.zstd)
- LZ4/Zstandard archives [md5-c6a611ce.zstd](md5-c6a611ce.zstd) / [md5-c6a611ce.lz4](md5-c6a611ce.lz4)

- Wasm executables [md5-1.wasm](md5-1.wasm) / [md5-2.wasm](md5-2.wasm)


## HashClash

- PE executables [md5-1.exe](md5-1.exe) / [md5-2.exe](md5-2.exe)

ZIP-based formats:
- Office Open XML
  - DOCX [md5-1.docx](md5-1.docx) / [md5-2.docx](md5-2.docx)
  - PPTX [md5-1.pptx](md5-1.pptx) / [md5-2.pptx](md5-2.pptx)
  - XLSX [md5-1.xls](md5-1.xls) / [md5-2.xls](md5-2.xls)
- Open Container Format
  - EPUB [md5-1.epub](md5-1.epub) / [md5-2.epub](md5-2.epub)
- Open Packaging Conventions
  - XPS [md5-1.xps](md5-1.xps) / [md5-2.xps](md5-2.xps)
  - 3MF [md5-1.3mf](md5-1.3mf) / [md5-2.3mf](md5-2.3mf)


# SHA1 (Shattered)

- JPG in PDF [sha1-1.pdf](sha1-1.pdf) / [sha1-2.pdf](sha1-2.pdf)

<!--
ffmpeg -i md5-1.png -c:v libx264 -tune stillimage -crf 22 -framerate 1/5 -c:a copy no.mp4 -map_metadata -1
-->
