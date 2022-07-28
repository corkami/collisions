# Collisions examples


## MD5

[Wang](https://link.springer.com/chapter/10.1007/11426639_2) (2005): [wang1.bin](wang1.bin) / [wang2.bin](wang2.bin)

[Apop](https://link.springer.com/chapter/10.1007/978-3-540-79263-5_1) (2008): [apop-1.bin](apop-1.bin) / [apop-2.bin](apop-2.bin)

[Rogue CA](https://www.win.tue.nl/hashclash/rogue-ca/) (2008): [real](ca-real.der) / [rogue](ca-rogue.der)

[Flame](https://en.wikipedia.org/wiki/Flame_(malware)) (2012): [certificate](flame.der)


### FastColl

single frame GIF: [collision1.gif](collision1.gif) / [collision2.gif](collision2.gif) ([recording](gifFastColl.svg))


### UniColl

JPG: [collision1.jpg](collision1.jpg) / [collision2.jpg](collision2.jpg) - [tldr-1.jpg](tldr-1.jpg) / [tldr-2.jpg](tldr-2.jpg)

PDF: [collision1.pdf](collision1.pdf) / [collision2.pdf](collision2.pdf)

PNG:
- generic headers (not OS X compatible): [collision1.png](collision1.png) / [collision2.png](collision2.png) ([recording](pngGen.svg))
- specific headers (same metadata): [0a959025-1.png](0a959025-1.png) / [0a959025-2.png](0a959025-2.png) - [aac2423a-1.png](aac2423a-1.png) / [aac2423a-2.png](aac2423a-2.png) (recordings: [1-with UniColl](pngUniColl.svg) / [2-precomputed](pngSpec.svg))

JP2: [collision1.jp2](collision1.jp2) / [collision2.jp2](collision2.jp2)

MP4:
- generic header, 32b length (LTV): [collision1.mp4](collision1.mp4) / [collision2.mp4](collision2.mp4)
- generic header, 64b length (TLV): [collisionl1.mp4](collisionl1.mp4) / [collisionl2.mp4](collisionl2.mp4)
  - specific header: [collisions1.mp4](collisions1.mp4) / [collisions2.mp4](collisions2.mp4)

Strategies:
- Good/bad contents (gotta catch 'em all): [gcea1.png](gcea1.png) / [gcea2.png](gcea2.png)
- Valid/Invalid: [png-valid.png](png-valid.png) / [png-invalid.png](png-invalid.png)


#### Multiple UniColl

poeMD5 (not Adobe compatible by accident): [poeMD5_A.pdf](poeMD5_A.pdf) / [poeMD5_B.pdf](poeMD5_B.pdf)

ZIP: [collision1.zip](collision1.zip) / [collision2.zip](collision2.zip)


### HashClash

Zip-based:
- 3mf: [collision-1.3mf](collision-1.3mf) / [collision-2.3mf](collision-2.3mf)
- Epub: [colllision-1.epub](colllision-1.epub) / [colllision-2.epub](colllision-2.epub)
- Xps: [colllision-1.xps](colllision-1.xps) / [colllision-2.xps](colllision-2.xps)

PE: [collision1.exe](collision1.exe) / [collision2.exe](collision2.exe)


#### polycolls

- JPG / PE: [jpg-pe.exe](jpg-pe.exe) / [jpg-pe.jpg](jpg-pe.jpg)
- PE / PDF: [pepdf.exe](pepdf.exe) / [pepdf.pdf](pepdf.pdf)
- PNG / PDF: [png-pdf.pdf](png-pdf.pdf) / [png-pdf.png](png-pdf.png)
- PE / MP4 / PDF / PNG: [pileup.exe](pileup.exe) / [pileup.mp4](pileup.mp4) / [pileup.pdf](pileup.pdf) / [pileup.png](pileup.png)


## plain collisions

FastColl: [fastcoll1.bin](fastcoll1.bin) / [fastcoll2.bin](fastcoll2.bin)

HashClash 9 blocks [cpc1.bin](cpc1.bin) / [cpc2.bin](cpc2.bin) - [1 block](https://www.win.tue.nl/hashclash/SingleBlock/) (2009) [single-cpc1.bin](single-cpc1.bin) / [single-cpc2.bin](single-cpc2.bin)

[Single IPC](https://marc-stevens.nl/research/md5-1block-collision/) (2012): [single-ipc1.bin](single-ipc1.bin) / [single-ipc2.bin](single-ipc2.bin)


## SHA1 (Shattered)

JPGs in PDF:
- multiple clipped images: [shattered1.pdf](shattered1.pdf) / [shattered2.pdf](shattered2.pdf)

JPG as page contents (desktop only, not browser):
- as page content: [jpgpage1.pdf](jpgpage1.pdf) / [jpgpage2.pdf](jpgpage2.pdf)
- as image and page content: [dualjpg1.pdf](dualjpg1.pdf) / [dualjpg2.pdf](dualjpg2.pdf)

# others

- prefix-switching payload for HTML polyglot [polyglot.html](polyglot.html)
- JPG file with 20 custom scans [20scans.jpg](20scans.jpg)
