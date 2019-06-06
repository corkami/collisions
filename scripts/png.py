#!/usr/bin/env python

# a script to collide 2 PNGs via MD5


import sys
import struct

PNGSIG = "\x89PNG\r\n\x1a\n"

fn1, fn2 = sys.argv[1:3]

with open(fn1, "rb") as f:
  d1 = f.read()
with open(fn2, "rb") as f:
  d2 = f.read()

assert d1.startswith(PNGSIG)
assert d2.startswith(PNGSIG)

with open("png1.bin", "rb") as f:
  block1 = f.read()
with open("png2.bin", "rb") as f:
  block2 = f.read()

ascii_art = """
/==============\\
|*            *|
|  PNG IMAGE   |
|     with     |
|  identical   |
|   -prefix    |
| MD5 collision|
|              |
|  by          |
| Marc Stevens |
|  and         |
|Ange Albertini|
|  in 2018     |
|*            *|
\\==============/
BRK!
""".replace("\n", "").replace("\r","")

suffix = "".join([
    # C0-C7
    "RealHash", # the remaining of the mARC chunk

    # C8-1C3 the tricky fake chunk

    # the length, the type and the data should all take 0x100
      struct.pack(">I", 0x100 - 4*2 + len(d2[8:])),
      "jUMP",
      # it will cover all data chunks of d2,
      # and the 0x100 buffer
      ascii_art,
    "\xDE\xAD\xBE\xEF", # fake CRC for mARC

    # 1C8 - Img2 + 4
    d2[8:],
    "\x5E\xAF\x00\x0D", # fake CRC for jUMP after d2's IEND
    d1[8:],
  ])

with open("collision1.png", "wb") as f:
  f.write("".join([
    block1,
    suffix
    ]))

with open("collision2.png", "wb") as f:
  f.write("".join([
    block2,
    suffix
    ]))
